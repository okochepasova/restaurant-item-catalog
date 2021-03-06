BEGIN TRANSACTION;
DROP TABLE IF EXISTS "users" CASCADE;
CREATE TABLE "users" (
	name VARCHAR(80) NOT NULL, 
	id SERIAL, 
	email VARCHAR(250) NOT NULL, 
	picture VARCHAR(250), 
	PRIMARY KEY (id)
);
INSERT INTO "users" (name,id,email,picture) VALUES ('Robo Barista',1,'tinnyTim@udacity.com','https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png'),
 ('Olga Kochepasova',2,'kochepasovaolga@gmail.com','https://lh5.googleusercontent.com/-eNsS-okqKJk/AAAAAAAAAAI/AAAAAAAAABk/wkcwibmMST4/photo.jpg');
ALTER SEQUENCE users_id_seq RESTART WITH 3;

DROP TABLE IF EXISTS "restaurant" CASCADE;
CREATE TABLE "restaurant" (
	name VARCHAR(80) NOT NULL, 
	id SERIAL, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "users" (id)
);
INSERT INTO "restaurant" (name,id,user_id) VALUES ('Urban Burger',1,1),
 ('Super Stir Fry',2,1),
 ('Panda Garden',3,1),
 ('Thyme for That Vegetarian Cuisine ',4,1),
 ('Tony''s Bistro ',5,1),
 ('Andala''s',6,1),
 ('Auntie Ann''s Diner'' ',7,1),
 ('Cocina Y Amor ',8,1),
 ('State Bird Provisions',9,1),
 ('Papa&#39;s Pizzeria',10,2);
ALTER SEQUENCE restaurant_id_seq RESTART WITH 11;

DROP TABLE IF EXISTS "menu_item" CASCADE;
CREATE TABLE "menu_item" (
	name VARCHAR(80) NOT NULL, 
	id SERIAL, 
	course VARCHAR(250), 
	description VARCHAR(250), 
	price VARCHAR(8), 
	restaurant_id INTEGER, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(restaurant_id) REFERENCES restaurant (id), 
	FOREIGN KEY(user_id) REFERENCES "users" (id)
);
INSERT INTO "menu_item" (name,id,course,description,price,restaurant_id,user_id) VALUES ('Veggie Burger',1,'Entree','Juicy grilled veggie patty with tomato mayo and lettuce','$7.50',1,1),
 ('French Fries',2,'Appetizer','with garlic and parmesan','$2.99',1,1),
 ('Chicken Burger',3,'Entree','Juicy grilled chicken patty with tomato mayo and lettuce','$5.50',1,1),
 ('Chocolate Cake',4,'Dessert','fresh baked and served with ice cream','$3.99',1,1),
 ('Sirloin Burger',5,'Entree','Made with grade A beef','$7.99',1,1),
 ('Root Beer',6,'Beverage','16oz of refreshing goodness','$1.99',1,1),
 ('Iced Tea',7,'Beverage','with Lemon','$.99',1,1),
 ('Grilled Cheese Sandwich',8,'Entree','On texas toast with American Cheese','$3.49',1,1),
 ('Veggie Burger',9,'Entree','Made with freshest of ingredients and home grown spices','$5.99',1,1),
 ('Chicken Stir Fry',10,'Entree','With your choice of noodles vegetables and sauces','$7.99',2,1),
 ('Peking Duck',11,'Entree',' A famous duck dish from Beijing[1] that has been prepared since the imperial era. The meat is prized for its thin, crisp skin, with authentic versions of the dish serving mostly the skin and little meat, sliced in front of the diners by the cook','$25',2,1),
 ('Spicy Tuna Roll',12,'Entree','Seared rare ahi, avocado, edamame, cucumber with wasabi soy sauce ','15',2,1),
 ('Nepali Momo ',13,'Entree','Steamed dumplings made with vegetables, spices and meat. ','12',2,1),
 ('Beef Noodle Soup',14,'Entree','A Chinese noodle soup made of stewed or red braised beef, beef broth, vegetables and Chinese noodles.','14',2,1),
 ('Ramen',15,'Entree','a Japanese noodle soup dish. It consists of Chinese-style wheat noodles served in a meat- or (occasionally) fish-based broth, often flavored with soy sauce or miso, and uses toppings such as sliced pork, dried seaweed, kamaboko, and green onions.','12',2,1),
 ('Pho',16,'Entree','a Vietnamese noodle soup consisting of broth, linguine-shaped rice noodles called banh pho, a few herbs, and meat.','$8.99',3,1),
 ('Chinese Dumplings',17,'Appetizer','a common Chinese dumpling which generally consists of minced meat and finely chopped vegetables wrapped into a piece of dough skin. The skin can be either thin and elastic or thicker.','$6.99',3,1),
 ('Gyoza',18,'Entree','light seasoning of Japanese gyoza with salt and soy sauce, and in a thin gyoza wrapper','$9.95',3,1),
 ('Stinky Tofu',19,'Entree','Taiwanese dish, deep fried fermented tofu served with pickled cabbage.','$6.99',3,1),
 ('Veggie Burger',20,'Entree','Juicy grilled veggie patty with tomato mayo and lettuce','$9.50',3,1),
 ('Tres Leches Cake',21,'Dessert','Rich, luscious sponge cake soaked in sweet milk and topped with vanilla bean whipped cream and strawberries.','$2.99',4,1),
 ('Mushroom risotto',22,'Entree','Portabello mushrooms in a creamy risotto','$5.99',4,1),
 ('Honey Boba Shaved Snow',23,'Dessert','Milk snow layered with honey boba, jasmine tea jelly, grass jelly, caramel, cream, and freshly made mochi','$4.50',4,1),
 ('Cauliflower Manchurian',24,'Appetizer','Golden fried cauliflower florets in a midly spiced soya,garlic sauce cooked with fresh cilantro, celery, chilies,ginger & green onions','$6.95',4,1),
 ('Aloo Gobi Burrito',25,'Entree','Vegan goodness. Burrito filled with rice, garbanzo beans, curry sauce, potatoes (aloo), fried cauliflower (gobi) and chutney. Nom Nom','$7.95',4,1),
 ('Veggie Burger',26,'Entree','Juicy grilled veggie patty with tomato mayo and lettuce','$6.80',4,1),
 ('Shellfish Tower',27,'Entree','Lobster, shrimp, sea snails, crawfish, stacked into a delicious tower','$13.95',5,1),
 ('Chicken and Rice',28,'Entree','Chicken... and rice','$4.95',5,1),
 ('Mom''s Spaghetti',29,'Entree','Spaghetti with some incredible tomato sauce made by mom','$6.95',5,1),
 ('Choc Full O'' Mint (Smitten''s Fresh Mint Chip ice cream)',30,'Dessert','Milk, cream, salt, ..., Liquid nitrogen magic','$3.95',5,1),
 ('Tonkatsu Ramen',31,'Entree','Noodles in a delicious pork-based broth with a soft-boiled egg','$7.95',5,1),
 ('Lamb Curry',32,'Entree','Slow cook that thang in a pool of tomatoes, onions and alllll those tasty Indian spices. Mmmm.','$9.95',6,1),
 ('Chicken Marsala',33,'Entree','Chicken cooked in Marsala wine sauce with mushrooms','$7.95',6,1),
 ('Potstickers',34,'Appetizer','Delicious chicken and veggies encapsulated in fried dough.','$6.50',6,1),
 ('Nigiri Sampler',35,'Appetizer','Maguro, Sake, Hamachi, Unagi, Uni, TORO!','$6.75',6,1),
 ('Veggie Burger',36,'Entree','Juicy grilled veggie patty with tomato mayo and lettuce','$7.00',6,1),
 ('Chicken Fried Steak',37,'Entree','Fresh battered sirloin steak fried and smothered with cream gravy','$8.99',7,1),
 ('Boysenberry Sorbet',38,'Dessert','An unsettlingly huge amount of ripe berries turned into frozen (and seedless) awesomeness','$2.99',7,1),
 ('Broiled salmon',39,'Entree','Salmon fillet marinated with fresh herbs and broiled hot & fast','$10.95',7,1),
 ('Morels on toast (seasonal)',40,'Appetizer','Wild morel mushrooms fried in butter, served on herbed toast slices','$7.50',7,1),
 ('Tandoori Chicken',41,'Entree','Chicken marinated in yoghurt and seasoned with a spicy mix(chilli, tamarind among others) and slow cooked in a cylindrical clay or metal oven which gets its heat from burning charcoal.','$8.95',7,1),
 ('Veggie Burger',42,'Entree','Juicy grilled veggie patty with tomato mayo and lettuce','$9.50',7,1),
 ('Spinach Ice Cream',43,'Dessert','vanilla ice cream made with organic spinach leaves','$1.99',7,1),
 ('Super Burrito Al Pastor',44,'Entree','Marinated Pork, Rice, Beans, Avocado, Cilantro, Salsa, Tortilla','$5.95',8,1),
 ('Cachapa',45,'Entree','Golden brown, corn-based Venezuelan pancake; usually stuffed with queso telita or queso de mano, and possibly lechon. ','$7.99',8,1),
 ('Chantrelle Toast',46,'Appetizer','Crispy Toast with Sesame Seeds slathered with buttery chantrelle mushrooms','$5.95',9,1),
 ('Guanciale Chawanmushi',47,'Dessert','Japanese egg custard served hot with spicey Italian Pork Jowl (guanciale)','$6.95',9,1),
 ('Lemon Curd Ice Cream Sandwich',48,'Dessert','Lemon Curd Ice Cream Sandwich on a chocolate macaron with cardamom meringue and cashews','$4.25',9,1),
 ('Glass of Water',49,'Beverage','A tall glass of water, no ice, and entirely free. You are not allowed to keep the glass however.','$0.00',10,2),
 ('Empty Plate',50,'Entree','To be deleted.','$59.99',10,2);
ALTER SEQUENCE menu_item_id_seq RESTART WITH 51;
COMMIT;
