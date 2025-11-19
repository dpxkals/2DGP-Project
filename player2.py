from game_world import add_object, add_collision_pairs, remove_object
from Monk import Monk
from peasant import Peasant

player2 = None

def create_player2(char='peasant', start_pos=(1400,300), key_map=None, layer=1):
    """char: 'shadow' 또는 'peasant' 선택
       key_map: 인스턴스별 키 매핑 딕셔너리
    """
    global player2
    # 유연한 캐릭터 이름 허용: 'peasant', 'peasant1' 등 접두사 방식도 허용
    c = str(char).lower()
    if c.startswith('monk'):
        player2 = Monk(key_map=key_map)
    elif c.startswith('peasant'):
        player2 = Peasant(key_map=key_map)
    else:
        raise ValueError('Unknown character: ' + str(char))

    player2.x, player2.y = start_pos
    player2.player_id = '2p'
    add_object(player2, layer)
    return player2

def register_collision_with(opponent):
    # opponent에는 다른 플레이어 객체를 전달
    if not player2:
        raise RuntimeError('player2 not created')
    add_collision_pairs('1p:2p', opponent, player2)

def destroy_player2():
    global player2
    if player2:
        remove_object(player2)
        player2 = None
