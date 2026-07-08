from django.core.management.base import BaseCommand
from core.models import Room, Block

class Command(BaseCommand):
    help = 'Add 800 rooms: 8 blocks, 5 floors, 20 rooms each'

    def handle(self, *args, **kwargs):
        total_created = 0
        
        for block_num in range(1, 9): # BLOCK 01 hadi BLOCK 08
            block_name = f"BLOCK {block_num:02d}"
            try:
                block = Block.objects.get(name=block_name)
            except Block.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'{block_name} haipo. Tengeneza Blocks 8 kwanza'))
                return
                
            for floor_num in range(1, 6): # FLOOR 1 hadi 5
                rooms_to_create = []
                for room_num in range(1, 21): # ROOM 1 hadi 20
                    room_number = f"{floor_num}{room_num:02d}"
                    
                    rooms_to_create.append(
                        Room(
                            block=block,
                            room_number=room_number,
                            floor_number=floor_num,
                            capacity=6,
                            price_per_semester=200000.0,
                            has_communal_ensuite=True
                            # TUMEONDOA is_full=HAPA
                        )
                    )
                
                Room.objects.bulk_create(rooms_to_create)
                total_created += len(rooms_to_create)
                self.stdout.write(f'Vimeongezwa {len(rooms_to_create)} vyumba {block_name} Floor {floor_num}')

        self.stdout.write(self.style.SUCCESS(f'KAZI IMEISHA! Jumla vyumba {total_created} vimeongezwa'))
