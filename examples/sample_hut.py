def make_hut_here(side=7):
    # Make a square cursor around you.
    c = cursor_here().square(side)
    # Draw walls.
    trace(c, height=5, block=wood_planks)
    # A ceiling made of glass sounds nice.
    fill(c.move(0,5,0), block=glass)
    # Let's not forget an opening.
    door = c.center().move(side/2,0,0).grow(0,2)
    # Check the door is where we think it is.
    blink(door)
    # Yes it is, carve the door.
    trace(door, block=air, height=3)
