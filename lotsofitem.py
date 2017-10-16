#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(username='user 1', email='example@gmail.com', picture='picture 1')

session.add(user1)
session.commit()


category1 = Category(name='Action')

session.add(category1)
session.commit()

item1 = Item(name='TEKKEN 7',
             description='Discover the epic conclusion of the long-time clan warfare between members of the Mishima family. Powered by Unreal Engine 4, the legendary fighting game franchise fights back with stunning story-driven cinematic battles and intense duels that can be enjoyed with friends and rivals.',  # noqa
             price='$ 29.50',
             image_url='/uploads/tekken7.jpg',
             youtube_trailer_url='https://youtu.be/kKLCwDg2JLA',
             category=category1,
             user=user1)

session.add(item1)
session.commit()


item2 = Item(name='Grand Theft Auto V',
             description='Gunrunning - Play now in GTA Online and dominate the illegal arms trade across Southern San Andreas. Fortify a subterranean bunker, decimate your enemies in a Mobile Operations Center, wreak havoc in a new fleet of Weaponized Vehicles, and make your mark on the SA arms trade.',  # noqa
             price='$ 17.50',
             image_url='/uploads/gta5.jpg',
             youtube_trailer_url='https://youtu.be/QkkoHAzjnUs',
             category=category1,
             user=user1)

session.add(item2)
session.commit()


item3 = Item(name='Cat Quest',
             description='Cat Quest is an open world RPG set in the pawsome world of cats! In search of your catnapped sister you pounce into the massive continent of Felingard - a world crafted in the style of overworld maps of yore and purring with cat-tastic characters, stories, and puns!',  # noqa
             price='$ 7.50',
             image_url='/uploads/catquest.jpg',
             youtube_trailer_url='https://youtu.be/TZzn4wobgug',
             category=category1,
             user=user1)

session.add(item3)
session.commit()


category2 = Category(name='RPG')

session.add(category2)
session.commit()


item4 = Item(name='The Elder Scrolls V: Skyrim Special Edition',
             description='Winner of more than 200 Game of the Year Awards, Skyrim Special Edition brings the epic fantasy to life in stunning detail. The Special Edition includes the critically acclaimed game and add-ons with all-new features like remastered art and effects, volumetric god rays, dynamic depth of field, screen-space reflections, and more.',  # noqa
             price='$ 19.99',
             image_url='/uploads/skyrim.jpg',
             youtube_trailer_url='https://youtu.be/QpvM9uwOcUc',
             category=category2,
             user=user1)

session.add(item4)
session.commit()


item5 = Item(name='Fallout 4',
             description='Bethesda Game Studios, the award-winning creators of Fallout 3 and The Elder Scrolls V: Skyrim, welcome you to the world of Fallout 4 – their most ambitious game ever, and the next generation of open-world gaming.',  # noqa
             price='$ 21.50',
             image_url='/uploads/fallout4.jpg',
             youtube_trailer_url='https://youtu.be/GE2BkLqMef4',
             category=category2,
             user=user1)

session.add(item5)
session.commit()

category3 = Category(name='Strategy')

session.add(category3)
session.commit()


item6 = Item(name='Sid Meier\'s Civilization® V',
             description='Create, discover, and download new player-created maps, scenarios, interfaces, and more!',  # noqa
             price='$ 11.50',
             image_url='/uploads/civilization5.jpg',
             youtube_trailer_url='https://youtu.be/MRoYEBfM_3A',
             category=category3,
             user=user1)

session.add(item6)
session.commit()


item7 = Item(name='XCOM® 2',
             description='XCOM 2 is the sequel to the award-winning strategy game, XCOM: Enemy Unknown. Twenty years have passed since humanity lost the war against the alien invaders and a new world order now exists on Earth. After years of lurking in the shadows, XCOM forces must rise and eliminate the alien occupation.',  # noqa
             price='$ 39.50',
             image_url='/uploads/xcom2.jpg',
             youtube_trailer_url='https://youtu.be/ZlF4_o3qALo',
             category=category3,
             user=user1)

session.add(item7)
session.commit()

print('added menu items!')
