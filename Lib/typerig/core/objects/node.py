# MODULE: TypeRig / Core / Node (Object)
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2017-2021 	(http://www.kateliev.com)
# (C) Karandash Type Foundry 		(http://www.karandash.eu)
#------------------------------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies ------------------------
from __future__ import absolute_import, print_function, division
import copy

from typerig.core.func.geometry import ccw
from typerig.core.func.math import ratfrac, randomize

from typerig.core.objects.point import Point
from typerig.core.objects.transform import Transform

from typerig.core.func.utils import isMultiInstance
from typerig.core.objects.atom import Member, Container

# - Init -------------------------------
__version__ = '0.3.0'
node_types = {'on':'on', 'off':'off', 'curve':'curve', 'move':'move'}

# - Classes -----------------------------
class Node(Member): 
	def __init__(self, *args, **kwargs):
		super(Node, self).__init__(*args, **kwargs)
		self.parent = kwargs.get('parent', None)

		# - Basics
		if len(args) == 1:
			if isinstance(args[0], self.__class__): # Clone
				self.x, self.y = args[0].x, args[0].y

			if isinstance(args[0], (tuple, list)):
				self.x, self.y = args[0]

		elif len(args) == 2:
			if isMultiInstance(args, (float, int)):
				self.x, self.y = float(args[0]), float(args[1])
		
		else:
			self.x, self.y = 0., 0.

		self.angle = kwargs.get('angle', 0)
		self.transform = kwargs.get('transform', Transform())
		self.complex_math = kwargs.get('complex', True)

		# - Metadata
		self.type = kwargs.get('type', node_types['on'])
		self.name = kwargs.get('name', '')
		self.identifier = kwargs.get('identifier', None)
		self.smooth = kwargs.get('smooth', False)
		self.g2 = kwargs.get('g2', False)
		self.selected = kwargs.get('selected', False)

	# -- Internals ------------------------------
	def __repr__(self):
		return '<{}: x={}, y={}, type={}>'.format(self.__class__.__name__, self.x, self.y, self.type)

	# -- Properties -----------------------------
	@property
	def index(self):
		return self.idx

	@property
	def contour(self):
		return self.parent

	@property
	def point(self):
		return Point(self.x, self.y, angle=self.angle, transform=self.transform, complex=self.complex_math)

	@point.setter
	def point(self, other):
		if isinstance(other, (self.__class__, Point)):
			self.x = other.x 
			self.y = other.y 
			self.angle = other.angle 
			self.transform = other.transform 
			self.complex_math = other.complex_math 
	
	@property
	def clockwise(self):
		return ccw(self.prev.point.tuple, self.point.tuple, self.next.point.tuple)
		
	@property
	def is_on(self):
		return self.type == node_types['on']

	@property
	def next_on(self):
		assert self.parent is not None, 'Orphan Node: Cannot find Next on-curve node!'
		currentNode = self.next
		
		while currentNode is not None and not currentNode.is_on:
			currentNode = currentNode.next
		
		return currentNode

	@property
	def prev_on(self):
		assert self.parent is not None, 'Orphan Node: Cannot find Previous on-curve node!'
		currentNode = self.prev
		
		while currentNode is not None and not currentNode.is_on:
			currentNode = currentNode.prev
		
		return currentNode

	@property
	def triad(self):
		return (self.prev, self, self.next)

	@property
	def triad_on(self):
		return (self.prev_on, self, self.next_on)

	@property
	def triad_on_max_y(self):
		if self.next_on.point.y > self.prev_on.point.y:
			return self.next_on

		return self.prev_on

	@property
	def triad_on_min_y(self):
		if self.next_on.point.y < self.prev_on.point.y:
			return self.next_on

		return self.prev_on
	
	@property
	def distance_to_next(self):
		return self.distance_to(self.next)

	@property
	def distance_to_prev(self):
		return self.distance_to(self.prev)

	@property
	def distance_to_next_on(self):
		return self.distance_to(self.next_on)

	@property
	def distance_to_prev_on(self):
		return self.distance_to(self.prev_on)

	@property
	def angle_to_next(self):
		return self.angle_to(self.next)

	@property
	def angle_to_prev(self):
		return self.angle_to(self.prev)

	@property
	def angle_to_next_on(self):
		return self.angle_to(self.next_on)

	@property
	def angle_to_prev_on(self):
		return self.angle_to(self.prev_on)
	
	# - Functions ----------------------------
	def distance_to(self, other):
		return self.point.diff_to(other.point)

	def angle_to(self, other):
		return self.point.angle_to(other.point)

	def insert_after(self, time):
		time = float(time)

		if time == 0.:
			mew_node = self.clone
		elif time == 1.:
			mew_node = self.next_on.clone
		# TODO find interpolated node at time on Line or CubicBezier
			
		self.parent.insert(self.idx + 1, mew_node)
		return new.node

	def insert_before(self, time):
		if time == 1.:
			mew_node = self.clone
		elif time == 0.:
			mew_node = self.next_on.clone
		# TODO find interpolated node at time on Line or CubicBezier
			
		self.parent.insert(self.idx - 1, mew_node)
		return new.node

	def insert_after_distance(self, distance):
		return self.insert_after(ratfrac(distance, self.distance_to_next_on, 1.))

	def insert_before_distance(self, distance):
		return self.insert_before(1. - ratfrac(distance, self.distance_to_prev_on, 1.))

	def remove(self):
		return self.parent.pop(self.idx)

	def update(self):
		raise NotImplementedError

	# - Transformation -----------------------------------------------
	def reloc(self, new_x, new_y):
		'''Relocate the node to new coordinates'''
		self.point = Point(new_x, new_y)
	
	def shift(self, delta_x, delta_y):
		'''Shift the node by given amout'''
		self.point += Point(delta_x, delta_y)

	def smart_reloc(self, new_x, new_y):
		'''Relocate the node and adjacent BCPs to new coordinates'''
		self.smartShift(new_x - self.x, new_y - self.y)

	def smart_shift(self, delta_x, delta_y):
		'''Shift the node and adjacent BCPs by given amout'''
		
		if self.is_on:	
			for node, test in [(self.prev, not self.prev.is_on), (self, self.is_on), (self.next, not self.next.is_on)]:
				if test: node.shift(delta_x, delta_x)
		else:
			self.shift(delta_x, delta_x)

	def randomize(self, cx, cy, bleed_mode=0):
		'''Randomizes the node coordinates within given constrains cx and cy.
		Bleed control trough bleed_mode parameter: 0 - any; 1 - positive bleed; 2 - negative bleed;
		'''
		shift_x, shift_y = randomize(0, cx), randomize(0, cy)
		self.smartShift(shift_x, shift_y)
		
		if bleed_mode > 0:
			if (bleed_mode == 2 and not self.clockwise) or (bleed_mode == 1 and self.clockwise):
				self.smartShift(-shift_x, -shift_y)		

	
	# -- IO Format ------------------------------
	@property
	def string(self):
		x = int(self.x) if isinstance(self.x, float) and self.x.is_integer() else self.x
		y = int(self.y) if isinstance(self.y, float) and self.y.is_integer() else self.y
		return '{0}{2}{1}'.format(x, y, ' ')

	def to_VFJ(self):
		node_config = []
		node_config.append(self.string)
		if self.smooth: node_config.append('s')
		if not self.is_on: node_config.append('o')
		if self.g2: node_config.append('g2')

		return ' '.join(node_config)

	@staticmethod
	def from_VFJ(string):
		string_list = string.split(' ')
		node_smooth = True if len(string_list) >= 3 and 's' in string_list else False
		node_type = node_types['off'] if len(string_list) >= 3 and 'o' in string_list else node_types['on']
		node_g2 = True if len(string_list) >= 3 and 'g2' in string_list else False

		return Node(float(string_list[0]), float(string_list[1]), type=node_type, smooth=node_smooth, g2=node_g2, name=None, identifier=None)

	@staticmethod
	def to_XML(self):
		raise NotImplementedError

	@staticmethod
	def from_XML(string):
		raise NotImplementedError


if __name__ == '__main__':
	# - Test initialization, normal and rom VFJ
	n0 = Node.from_VFJ('10 20 s g2')
	n1 = Node.from_VFJ('20 30 s')
	n2 = Node(35, 55.65)
	n3 = Node(44, 67, type='smooth')
	n4 = Node(n3)
	print(n3, n4)
	
	# - Test math and VFJ export
	n3.point = Point(34,88)
	n3.point += 30
	print(n3.to_VFJ())
	
	# - Test Containers and VFJ export 
	c = Container([n0, n1, n2, n3, n4], default_factory=Node)
	c.append((99,99))
	print(n0.next)
	
