import collections


class ConsumableList(collections.deque):

    def consume(self, n):
        return [self.popleft() for _ in range(n)]


WORDS = ConsumableList([
    'Africa', 'Agent', 'Air', 'Alien', 'Alps', 'Amazon', 'Ambulance', 'America', 'Angel',
    'Antarctica', 'Apple', 'Arm', 'Atlantis', 'Australia', 'Aztec', 'Back', 'Ball', 'Band', 'Bank',
    'Bar', 'Bark', 'Bat', 'Battery', 'Beach', 'Bear', 'Beat', 'Bed', 'Beijing', 'Bell', 'Belt',
    'Berlin', 'Bermuda', 'Berry', 'Bill', 'Block', 'Board', 'Bolt', 'Bomb', 'Bond', 'Boom', 'Boot',
    'Bottle', 'Bow', 'Box', 'Bridge', 'Brush', 'Buck', 'Buffalo', 'Bug', 'Bugle', 'Button', 'Calf',
    'Canada', 'Cap', 'Capital', 'Car', 'Card', 'Carrot', 'Casino', 'Cast', 'Cat', 'Cell',
    'Centaur', 'Center', 'Chair', 'Change', 'Charge', 'Check', 'Chest', 'Chick', 'China',
    'Chocolate', 'Church', 'Circle', 'Cliff', 'Cloak', 'Club', 'Code', 'Cold', 'Comic', 'Compound',
    'Concert', 'Conductor', 'Contract', 'Cook', 'Copper', 'Cotton', 'Court', 'Cover', 'Crane',
    'Crash', 'Cricket', 'Cross', 'Crown', 'Cycle', 'Czech', 'Dance', 'Date', 'Day', 'Death',
    'Deck', 'Degree', 'Diamond', 'Dice', 'Dinosaur', 'Disease', 'Diver', 'Doctor', 'Dog', 'Draft',
    'Dragon', 'Dress', 'Drill', 'Drop', 'Duck', 'Dwarf', 'Eagle', 'Egypt', 'Embassy', 'Engine',
    'England', 'Europe', 'Eye', 'Face', 'Fair', 'Fall', 'Fan', 'Fence', 'Field', 'Fighter',
    'Figure', 'File', 'Film', 'Fire', 'Fish', 'Flute', 'Fly', 'Foot', 'Force', 'Forest', 'Fork',
    'France', 'Game', 'Gas', 'Genius', 'Germany', 'Ghost', 'Giant', 'Glass', 'Glove', 'Gold',
    'Grace', 'Grass', 'Greece', 'Green', 'Ground', 'Ham', 'Hand', 'Hawk', 'Head', 'Heart',
    'Helicopter', 'Himalayas', 'Hole', 'Hollywood', 'Honey', 'Hood', 'Hook', 'Horn', 'Horse',
    'Horseshoe', 'Hospital', 'Hotel', 'Ice', 'India', 'Iron', 'Ivory', 'Jack', 'Jam', 'Jet',
    'Jupiter', 'Kangaroo', 'Ketchup', 'Key', 'Kid', 'King', 'Kiwi', 'Knife', 'Knight', 'Lab',
    'Lap', 'Laser', 'Lawyer', 'Lead', 'Lemon', 'Leprechaun', 'Life', 'Light', 'Limousine', 'Line',
    'Link', 'Lion', 'Litter', 'Lock', 'Log', 'London', 'Luck', 'Mail', 'Mammoth', 'Maple',
    'Marble', 'March', 'Mass', 'Match', 'Mercury', 'Mexico', 'Microscope', 'Millionaire', 'Mine',
    'Mint', 'Missile', 'Model', 'Mole', 'Moon', 'Moscow', 'Mount', 'Mouse', 'Mouth', 'Mug', 'Nail',
    'Needle', 'Net', 'New', 'Night', 'Ninja', 'Note', 'Novel', 'Nurse', 'Nut', 'Octopus', 'Oil',
    'Olive', 'Olympus', 'Opera', 'Orange', 'Organ', 'Palm', 'Pan', 'Pants', 'Paper', 'Parachute',
    'Park', 'Part', 'Pass', 'Paste', 'Penguin', 'Phoenix', 'Piano', 'Pie', 'Pilot', 'Pin', 'Pipe',
    'Pirate', 'Pistol', 'Pit', 'Pitch', 'Plane', 'Plastic', 'Plate', 'Platypus', 'Play', 'Plot',
    'Point', 'Poison', 'Pole', 'Police', 'Pool', 'Port', 'Post', 'Pound', 'Press', 'Princess',
    'Pumpkin', 'Pupil', 'Pyramid', 'Queen', 'Rabbit', 'Racket', 'Ray', 'Revolution', 'Ring',
    'Robin', 'Robot', 'Rock', 'Rome', 'Root', 'Rose', 'Roulette', 'Round', 'Row', 'Ruler',
    'Satellite', 'Saturn', 'Scale', 'School', 'Scientist', 'Scorpion', 'Screen', 'Scuba', 'Seal',
    'Server', 'Shadow', 'Shakespeare', 'Shark', 'Ship', 'Shoe', 'Shop', 'Shot', 'Sink',
    'Skyscraper', 'Slip', 'Slug', 'Smuggler', 'Snow', 'Snowman', 'Sock', 'Soldier', 'Soul',
    'Sound', 'Space', 'Spell', 'Spider', 'Spike', 'Spine', 'Spot', 'Spring', 'Spy', 'Square',
    'Stadium', 'Staff', 'Star', 'State', 'Stick', 'Stock', 'Straw', 'Stream', 'Strike', 'String',
    'Sub', 'Suit', 'Superhero', 'Swing', 'Switch', 'Table', 'Tablet', 'Tag', 'Tail', 'Tap',
    'Teacher', 'Telescope', 'Temple', 'Theater', 'Thief', 'Thumb', 'Tick', 'Tie', 'Time', 'Tokyo',
    'Tooth', 'Torch', 'Tower', 'Track', 'Train', 'Triangle', 'Trip', 'Trunk', 'Tube', 'Turkey',
    'Undertaker', 'Unicorn', 'Vacuum', 'Van', 'Vet', 'Wake', 'Wall', 'War', 'Washer', 'Washington',
    'Watch', 'Water', 'Wave', 'Web', 'Well', 'Whale', 'Whip', 'Wind', 'Witch', 'Worm', 'Yard',
    'York'
])
