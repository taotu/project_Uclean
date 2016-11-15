UCleaners is an online platform that provides quality on-demand pickup and delivery service for laundry and dry cleaning. The idea is to make doing laundry easy and quick for the New Yorkers. On UCleaners you can browse local laundromats, view ratings, read reviews, and prices. Future implementation is mobile applications for iOS and Android to schedule for  drop off, delivery or pickup. The process is simple sign up online with your information: First and last name, email and password. Browse and pick your laundromat. Schedule a pick up, drop off and/or the delivery. Confirm your address, enter your mode of payment and place your order.
        The application will include common entities like Customer with attributes like name,address, phone number and email. Customers can place Orders which has OrderItems. The OrderItems entity contains cloth Items. Once an Order is placed and paid for, the Payment information goes to an OrderPayment entity  and Admin account or Laundromat owner can process and validate the Order. Each order is process by exactly one Admin and Laundromat.

 pip install click, flask, sqlalchemy and psycop2

Run it in the shell:
        python Ucleaner.py
