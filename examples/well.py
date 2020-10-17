def make_well(c):
  fill(c, block=stone_brick)
  corners = c.corners()
  c = c.shrink(1,1)
  fill(c, block=water_stationary)
  trace(corners, block=stone_brick, height=3)
  corners = corners.move(0,3,0)
  trace(corners, block=torch_up)
  c = c.move(0,3,0)
  fill(c, block=stone_brick)
  c = c.center().move(0,1,0)
  trace(c, block=torch_up)


