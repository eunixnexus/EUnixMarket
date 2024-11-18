import EUnix as mp






for i in range(3): #market slot
    mar= mp.Market()
#(User, User_id, Order_id, energy_qty, energy_rate, bid_offer_time, delivery_time,type, attributes, requirements, power, area, direction)
    mar.accept_order("Chris", "a2a2", 1, 100, 30, "20min","30min", True) 
    mar.accept_order("Uche", "a2a3", 2, 200, 20, "20min","30min", True) 
    mar.accept_order("Chika", "a2a5", 3, 100, 15, "20min","30min", True) #150
    mar.accept_order("Chekas", "a2a6", 4, 50, 10, "20min","30min", True) 

    mar.accept_order("Ngozi", "a3a4", 5, 100, 5, "20min","30min", False) 
    mar.accept_order("Ebere", "a3a3", 6, 200, 10, "20min","30min", False) 
    mar.accept_order("Amuche", "a3a4", 7, 50, 15, "20min","30min", False) 
    mar.accept_order("Nkem", "a3a5", 8, 60, 15, "20min","30min", False) 
    mar.accept_order("Uka", "a3a6", 9, 150, 25, "20min","30min", False)



#bids = mar.get_oders()
#print (bids)
transactions, extras = mar.run('uniform')
trans_df = transactions.get_df()
print(trans_df)




