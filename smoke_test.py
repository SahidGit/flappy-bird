# Minimal smoke test for non-UI game logic
# This test avoids opening a window. It imports classes and runs small checks.
from flappy import Bird, Pipe, PIPE_WIDTH, WIDTH, HEIGHT, GROUND_HEIGHT

errors = []

# Create bird and ensure initial state
b = Bird()
if not (0 < b.y < HEIGHT):
    errors.append('Bird initial y out of bounds')

# Create a pipe and simulate movement
p = Pipe(WIDTH + 40)
old_x = p.x
p.update(3.0)
if p.x >= old_x:
    errors.append('Pipe did not move left on update')

# Verify rects produce sensible values
top, bot = p.rects()
if top.width != PIPE_WIDTH or bot.width != PIPE_WIDTH:
    errors.append('Pipe rect widths incorrect')

# Simple collision test: place bird inside top rect and ensure collision
b.x = p.x + PIPE_WIDTH // 2
b.y = p.top / 2
if not b.get_rect().colliderect(top):
    errors.append('Collision detection failed for top pipe')

# Ground collision test
b.y = HEIGHT - GROUND_HEIGHT + 10
if b.get_rect().bottom <= HEIGHT - GROUND_HEIGHT:
    errors.append('Ground collision detection failed')

if errors:
    print('SMOKE TEST FAILED')
    for e in errors:
        print('-', e)
    raise SystemExit(1)
print('SMOKE TEST PASSED')
