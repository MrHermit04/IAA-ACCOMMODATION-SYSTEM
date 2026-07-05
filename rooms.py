from decimal import Decimal
from core.models import Block, Room

rooms = []
for floor in range(1, 6):
    for room_num in range(1, 21):
        room_id = f"F{floor}-R{room_num}"
        rooms.append(room_id)

block = Block.objects.get(name="Block 01")
Room.objects.filter(block=block).delete()

for room_id in rooms:
    floor_num = int(room_id.split('-')[0][1:])
    Room.objects.create(block=block, room_number=room_id, capacity=6, price_per_semester=Decimal("200000.00"), floor_number=floor_num, has_communal_ensuite=False)

