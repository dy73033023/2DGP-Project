world = [[] for _ in range(4)]

def add_object(o, depth = 0):
    world[depth].append(o)


def add_objects(ol, depth = 0):
    world[depth] += ol


def update():
    for layer in world:
        for o in layer:
            o.update()


def render():
    for layer in world:
        for o in layer:
            o.draw()

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            # collision_pairs 해당 오브젝트를 제거
            remove_collision_object(o)
            return

    raise ValueError('Cannot delete non existing object')


def clear():
    global world

    for layer in world:
        layer.clear()

# 기존 collide는 유지하지만, 그룹별로 다른 BB를 쓰는 전용 함수를 추가한다.
def _get_group_bb(obj, group: str, is_first: bool):
    # sword:player2 형태에서 첫 번째는 공격자(칼), 두 번째는 피격자(몸)
    if group.startswith('sword:') and is_first:
        # 공격 박스가 있으면 우선 사용
        if hasattr(obj, 'get_attack_bb'):
            bb = obj.get_attack_bb()
            if bb:
                return bb
    # 기본은 몸통 박스
    return obj.get_bb()


def _rects_overlap(a_rect, b_rect):
    left_a, bottom_a, right_a, top_a = a_rect
    left_b, bottom_b, right_b, top_b = b_rect

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True

collision_pairs = {}
def add_collision_pair(group, a, b):
    if group not in collision_pairs: # 처음 추가되는 그룹이면
        collision_pairs[group] = [ [], [] ] # 해당 그룹을 만든다
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)
    return None

def handle_collision():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                a_bb = _get_group_bb(a, group, True)
                b_bb = _get_group_bb(b, group, False)
                if _rects_overlap(a_bb, b_bb):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)
    return None

def update_collision_pair(group, a, b):
    if group in collision_pairs:
        # a 또는 b가 None이면 해당 리스트 비우기 (공격 종료 등)
        if a is None:
            collision_pairs[group][0].clear()
        else:
            collision_pairs[group][0] = [a] if not isinstance(a, list) else a
        if b is None:
            collision_pairs[group][1].clear()
        else:
            collision_pairs[group][1] = [b] if not isinstance(b, list) else b

# collision_pairs에 들어있는 모든 o를 제거
def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)