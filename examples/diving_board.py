def diving_board(height=10, depth=5):
  """Draw a diving board, as tall as you dare."""
  c = cursor_here()
  # Tall colums, with ladder
  trace(c.move(0,0,1), block=wood_oak, height=10)
  trace(c,ladder, height=10)
  # Board on the top (with slabs, to make it more board-like).
  for x in range(1,4):
    trace(c.move(0,10,x), block=wooden_slab)
  # Pool at the bottom. Don't miss it!
  pool = c.move(0,-depth,5).grow(1,1)
  trace(pool.grow(1,1), wood_oak, height=depth)
  fill(pool, water, height=depth)
