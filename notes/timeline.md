
- user envia nickname e pub_key pra parea
- parea envia o resultado

- caller envia "ready" para a parea
- parea bloqueia novos players e manda (seq, nick, pub_key) para o call assinar
- caller envia "start" para parea com (seq, nick, pub_key) assinadas
- parea envia "start" para os players

- players geram as simetric keys
- players enviam o "card" para a parea
- parea envia o "card" para todos

- quando o caller tiver todos os cards, envia o "deck" para a parea
- parea envia o "deck" para um player de cada vez para o shuffle e para o caller
- quando tiver passado por todos, parea envia o "deck" para o caller

- caller envia o "final deck" para a parea
- parea envia o "final deck" para todos

- todos enviam as simetric keys para a parea
- parea envia as simetric keys para todos

- os players enviam os "winners" para a parea
- parea envia os "winners" para o caller
- depois de receber os "winners", o caller envia o "final winners" para a parea
- parea envia o "final winners" para todos