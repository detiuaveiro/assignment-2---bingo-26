
1. registar com nickname e pub_key (user -> parea)
2. resultado do registo (parea -> user)

1. caller envia "start" para parea
2. parea envia todas as pub_keys para todos
3. parea envia "start" para os players
4. players enviam o "card" para a parea
5. parea envia o "card" para todos
6. quando o caller tiver todos os cards, envia o "deck" para a parea
7. parea envia o "deck" para um player de cada vez para o shuffle
8. quando tiver passado por todos, parea envia o "deck" para o caller
9. caller envia o "final deck" para a parea
10. parea envia o "final deck" para todos
11. todos enviam as simetric keys para a parea
12. parea envia as simetric keys para todos
13. os players enviam os "winners" para a parea
14. parea envia os "winners" para o caller
15. depois de receber os "winners", o caller envia o "final winners" para a parea
16. parea envia o "final winners" para todos