from game_world import add_object, add_collision_pairs, remove_object
from Monk import Monk
from peasant import Peasant

player1 = None

def create_player1(char='monk', start_pos=(500,300), key_map=None, layer=1):
    """char: 'shadow' 또는 'peasant' 선택
       key_map: 인스턴스별 키 매핑 딕셔너리
    """
    global player1
    if char == 'monk':
        player1 = Monk(key_map=key_map)
    elif char == 'peasant':
        player1 = Peasant(key_map=key_map)
    else:
        raise ValueError('Unknown character: ' + str(char))

    player1.x, player1.y = start_pos
    player1.player_id = '1p'
    add_object(player1, layer)
    return player1

def register_collision_with(opponent):
    # opponent에는 다른 플레이어 객체를 전달
    if not player1:
        raise RuntimeError('player1 not created')
    add_collision_pairs('1p:2p', player1, opponent)

def destroy_player1():
    global player1
    if player1:
        remove_object(player1)
        player1 = None
