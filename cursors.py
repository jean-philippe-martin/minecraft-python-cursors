# This library is meant to be used with Minecraft Python.
# It gives you a nice little cursor abstraction to draw with.

# Use it like this:
#
# from mcpi.minecraft import Minecraft
# from cursors import *
# from blocks import *
# mc=Minecraft.create('192.168.1.1')
# minecraft_connection(mc)
#
# (replace 192.168.1.1 with your RaspberryJuice-enabled Minecraft server's
# IP address)

# Then for example to draw a square:
#
# square = cursor_here().square(3)
# trace(square, block=stone)

# If you see this error:
# AttributeError: 'NoneType' object has no attribute 'player'
# Double-check you didn't forget to call minecraft_connection.

import time

# This will hold the connection to Minecraft.
# Update it by calling minecraft_connection.
mc = None

class Stencil:
    """A bunch of blocks, copy/pasted from the game."""
    def __init__(self, rectangle_cursor, height, blocks):
        self.rectangle_cursor = rectangle_cursor
        self.height = height
        self.blocks = blocks
    def __repr__(self):
        return 'Stencil({}, {}, {})'.format(
            self.rectangle_cursor.__repr__(),
            self.height,
            self.blocks)
    def move(self, dx, dy, dz):
        """Move the draw area, leaving its size unchanged."""
        return Stencil(self.rectangle_cursor.move(dx, dy, dz), self.height, self.blocks)
    def boundary(self, height=None):
        if height: raise ValueError('Cannot specify height when tracing Stencil.')
        return self.rectangle_cursor.boundary(height=self.height)
    def interior(self, height=None):
        if height: raise ValueError('Cannot specify height when filling Stencil.')
        return self.rectangle_cursor.interior(height=self.height)
    def paste(self):
        """Paste the blocks at the current position."""
        index = 0;
        for j in range(self.rectangle_cursor.y, self.rectangle_cursor.y + self.height):
            for i in range(self.rectangle_cursor.x, self.rectangle_cursor.x + self.rectangle_cursor.x_width):
                for k in range(self.rectangle_cursor.z, self.rectangle_cursor.z + self.rectangle_cursor.z_depth):
                    mc.setBlock(i, j, k, self.blocks[index])
                    index += 1
    def cursor(self):
        """The underlying cursor."""
        return self.rectangle_cursor


class PointCursor:
    def __init__(self, x, y ,z):
        self.x = x
        self.y = y
        self.z = z
    def __repr__(self):
        return 'PointCursor({},{},{})'.format(self.x, self.y, self.z)
    def move(self, dx, dy, dz):
        """Move the point by this much."""
        return PointCursor(self.x+dx, self.y+dy, self.z+dz)
    def grow(self, dx, dz):
        """Grow by this amount in both directions."""
        return RectangleCursor(self.x, self.y, self.z, 1, 1).grow(dx, dz)
    def rectangle(self, width, depth):
        """RectangleCursor of the specified size, centered on this cursor."""
        return RectangleCursor(self.x-width/2, self.y, self.z-depth/2, width, depth)
    def square(self, side):
        return self.rectangle(side, side)
    def circle(self, radius):
        return CircleCursor(self.x, self.y, self.z, radius)
    def center(self):
        """The center point, so here it's the point itself of course."""
        return self
    def boundary(self, height=1):
        if not height: height=1
        return [(self.x, self.y+h, self.z) for h in range(height)]
    def interior(self):
        return self.boundary();
    def bounding_rectangle(self, other=None):
        """RectangleCursor that contains this cursor (and 'other', if specified)."""
        return self.rectangle(1,1).bounding_rectangle(other)


class CursorList:
    def __init__(self, cursors):
        # Make a copy of the list.
        self.cursors = cursors[:]
    def __repr__(self):
        return 'CursorList[{}])'.format(len(self.cursors))
    def __len__(self):
        return len(self.cursors)
    def move(self, dx, dy, dz):
        moved_cursors = [c.move(dx, dy, dz) for c in self.cursors]
        return CursorList(moved_cursors)
    def each(self, function):
        return CursorList([function(cursor) for cursor in self.cursors])
    def rectangle(self, width, depth):
        return self.each(lambda cursor: cursor.rectangle(width, depth))
    def square(self, side):
        return self.each(lambda cursor: cursor.square(side))
    def center(self):
        """The center point, computed as center of the bounding box."""
        return self.bounding_rectangle().center()
    def grow(self, dx, dz):
        return self.each(lambda cursor: cursor.grow(dx, dz))
    def shrink(self, dx, dz):
        return self.each(lambda cursor: cursor.shrink(dx, dz))
    def boundary(self, height=1):
        if not height: height=1
        for cursor in self.cursors:
            for xyz in cursor.boundary(height=height): yield xyz
    def interior(self):
        for cursor in self.cursors:
            for xyz in cursor.interior(): yield xyz
    def bounding_rectangle(self, other=None):
        """RectangleCursor that contains this cursor (and 'other', if specified)."""
        for cursor in self.cursors:
            other = cursor.bounding_rectangle(other)
        return other


class RectangleCursor:
    def __init__(self, x, y, z, x_width, z_depth):
        """(x,y,z) is lowest-coordinate point, we add width and depth to that."""
        self.x = x
        self.y = y
        self.z = z
        if x_width<1: x_width=1
        if z_depth<1: z_depth=1
        self.x_width = x_width
        self.z_depth = z_depth
    def __repr__(self):
        return 'RectangleCursor({},{},{},{},{})'.format(self.x, self.y, self.z, self.x_width, self.z_depth)
    def move(self, dx, dy, dz):
        """Move the rectangle, leaving its size unchanged."""
        return RectangleCursor(self.x+dx, self.y+dy, self.z+dz, self.x_width, self.z_depth)
    def shrink(self, dx, dz):
        """Shrink all sides by the specified amounts (negatives ok)."""
        if dx==dz==0: return self
        if self.x_width - 2*dx < 1:
            dx = (self.x_width)//2
        if self.z_depth - 2*dz < 1:
            dz = (self.z_depth)//2
        return RectangleCursor(self.x+dx, self.y, self.z+dz, max(1,self.x_width-2*dx), max(1,self.z_depth-2*dz))
    def grow(self, dx, dz):
        """Grow all sides by the specified amounts (negatives ok)."""
        return self.shrink(-dx, -dz)
    def center(self):
        """The center point (as a cursor)."""
        return PointCursor(self.x+self.x_width/2, self.y, self.z+self.z_depth/2)
    def corners(self):
        """Corners. 4 for a proper rectangle, 2 for a line, 1 for a point."""
        corner_coords = [
          (self.x, self.y, self.z)
        ]
        if self.x_width > 1:
            corner_coords.append(
                (self.x + self.x_width - 1, self.y, self.z) )
            if self.z_depth > 1:
                corner_coords.append(
                    (self.x + self.x_width - 1, self.y, self.z + self.z_depth - 1))
        if self.z_depth > 1:
            corner_coords.append(
                (self.x, self.y, self.z + self.z_depth - 1))
        return CursorList([PointCursor(x,y,z) for x,y,z in corner_coords])
    def side(self, dx, dz):
        """Given a direction, get that side of the rectangle (a line, returned as a RectangleCursor)."""
        if (dx==dz==0): return self.center()
        if (dx and dz): raise ValueError('Direction cannot be diagonal.')
        width = self.x_width if dx==0 else 1
        depth = self.z_depth if dz==0 else 1
        start_x = self.x
        if dx>0: start_x = self.x + self.x_width - 1
        start_z = self.z
        if dz>0: start_z = self.z + self.z_depth - 1
        return RectangleCursor(start_x, self.y, start_z, width, depth)
    def boundary(self, height=1):
        """All the coordinates on the boundary."""
        if not height: height=1
        for i in range(self.x, self.x + self.x_width):
            yield (i, self.y, self.z)
        for j in range(self.z, self.z + self.z_depth):
            yield (self.x + self.x_width - 1, self.y, j)
        if self.z_depth>1:
            for i in range(0, self.x_width):
                yield (self.x + self.x_width - i - 1, self.y, self.z + self.z_depth - 1)
        if self.x_width>1:
            for j in range(0, self.z_depth):
                yield (self.x, self.y, self.z + self.z_depth - j - 1)
        if height>1:
            for xyz in self.corners().move(0,1,0).boundary(height-1):
                yield xyz
    def interior(self):
        """All the coordinates on the boundary or inside it."""
        for i in range(self.x, self.x + self.x_width):
            for k in range(self.z, self.z + self.z_depth):
                yield (i, self.y, k)
    def bounding_rectangle(self, other=None):
        """RectangleCursor that contains this cursor and 'other' (if specified)."""
        if not other: return self
        other = other.bounding_rectangle()
        x1 = min(self.x, other.x)
        y1 = min(sely.y, other.y)
        z1 = min(self.z, other.z)
        x2 = max(self.x + self.x_width, other.x + other.x_width)
        y2 = max(self.y, other.y)
        z2 = max(self.z + self.z_depth, other.z + other.z_depth)
        return RectangleCursor(x1,y1,z1, (x2-x1), (z2-z1))
    def copy(self, height):
        """Copy the blocks inside the selected rectangular volume."""
        blocks = mc.getBlocks(self.x, self.y, self.z, self.x+self.x_width-1, self.y+height-1, self.z+self.z_depth-1)
        return Blocks(self, height, blocks)


class CircleCursor:
    def __init__(self, x, y, z, radius):
        """(x,y,z) is the center point."""
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
    def move(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
    def grow(self, dr):
        ret = CircleCursor(self.x, self.y, self.z, self.radius)
        ret.radius += dr
        if ret.radius<1: ret.radius=1
        return ret
    def shrink(self, dr):
        return self.grow(-dr)
    def center(self):
        return PointCursor(self.x, self.y, self.z)
    def interior(self):
        """Lists coordinates at the edge or inside of the circle."""
        for x in range(0, self.radius+1):
            for z in range(0, self.radius+1):
                dist = sqr(x) + sqr(z)
                if (dist<sqr(self.radius)):
                    yield (self.x + x, self.y, self.z + z)
                    if x>0:
                        yield (self.x - x, self.y, self.z + z)
                    if z>0:
                        yield (self.x + x, self.y, self.z - z)
                    if x>0 and z>0:
                        yield (self.x - x, self.y, self.z - z)
    def boundary(self, height=1):
        """Lists coordinates at the edge of the circle."""
        if not height: height=1
        coords = set(self.interior())
        for (x,y,z) in coords:
            if ((x+1,y,z) not in coords or
               (x-1,y,z) not in coords or
               (x,y,z+1) not in coords or
               (x,y,z-1) not in coords):
               for h in range(height): yield (x,y+h,z)
    def bounding_rectangle(self, other=None):
        """RectangleCursor that contains the circle (and 'other', if specified)."""
        rectangle = RectangleCursor(self.x-self.radius+1, self.y, self.z-self.radius+1,
            self.radius*2-1, self.radius*2-1)
        return rectangle.bounding_rectangle(other)


def minecraft_connection(new_mc):
    """Pass the Minecraft connection to enable cursor_here() and related."""
    global mc
    mc = new_mc

def rounded_pos(xyz):
    x0,y0,z0 = xyz
    return int(x0), int(y0), int(z0)

def sqr(n):
    return n*n

def rounded_player_pos():
    """Current player position, as whole numbers."""
    return rounded_pos(mc.player.getPos())

def put_here(block=112):
    """Put a block of this type next to the player."""
    x,y,z = rounded_player_pos()
    mc.setBlock(x,y,z,block)

def cursor_here():
    global mc
    x,y,z = rounded_pos(mc.player.getPos())
    return PointCursor(x,y,z)

def cursor_nearby(block=112):
    """Find the nearest block of this type and return a cursor there."""
    global mc
    x,y,z = rounded_pos(mc.player.getPos())
    best_dist=999
    best_cur=None
    size=4
    # This is much faster than calling getBlock repeatedly.
    blocks = mc.getBlocks(x-size, y-size, z-size, x+size-1, y+size-1, z+size-1)
    index = 0
    for j in range(y-size, y+size):
        for i in range(x-size, x+size):
            for k in range(z-size, z+size):
                b = blocks[index]
                index += 1
                if b != block: continue
                dist = sqr(i-x) + sqr(j-y) + sqr(k-z)
                if dist > best_dist: continue
                best_dist = dist
                best_cur = PointCursor(i,j,k)
    return best_cur

def trace(cursor, block=1, height=1, stride=1):
    """Draw on the outline of the cursor."""
    count=0
    for (x,y,z) in cursor.boundary():
        count += 1
        if (count % stride) != 0: continue
        for h in range(height):
            mc.setBlock(x,y+h,z, block)

def fill(cursor, block=1, height=1):
    """Fill the area of the cursor and inside it."""
    for (x,y,z) in cursor.interior():
        for h in range(height):
            mc.setBlock(x,y+h,z, block)

def fill_except(cursor, height, cursor_except, height_except, block=1):
    """Fill the area that is inside the cursor but not inside cursor_except."""
    places = {
        (x,y+h,z): block for (x,y,z) in cursor.interior() for h in range(height)
    }
    for (x,y,z) in cursor_except.interior():
        for h in range(height_except):
            if (x,y+h,z) in places:
                del places[(x,y+h,z)]
    for (x,y,z),b in places.items():
        mc.setBlock(x,y,z,b)

def blink(cursor, height=0, block=41):
    """Show the cursor, then hide it again."""
    positions = list(cursor.boundary(height=height))
    old_values = [mc.getBlock(x,y,z) for x,y,z in positions]
    for loop in range(3):
        for x,y,z in positions:
            mc.setBlock(x,y,z,block)
        time.sleep(1)
        for i in range(len(positions)):
            x,y,z = positions[i]
            mc.setBlock(x,y,z,old_values[i])
        time.sleep(1)

