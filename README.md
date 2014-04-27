ld29
====
Theme is "Beneath the surface"

Game
====

Mole digging to find things, trying to dig out as must gems as possible before
running out of time. Worms can add some times.

This is inspired from an actual game I played a while ago. I can't seem to
remember its name though.

Status
======

2014/04/27 - 11:30am
--------------------

* Going terraria style, keyboard+mouse ftw!
* mouse selection is ok, I need to add action on mouse click
* Jump and gravity are a bit odd, will fix later

2014/04/26 - 11pm
-----------------
* Sprites are mostly placeholders
* No sound, no music

* Can dig down using 'down' key. I need to implement a proper action for digging
  as it must be seperated from movements.

* No bonuses, no score, no timing

* No level boundaries

* Physics and movement need rework

Thoughts regarding basecode
===========================

Entities implementation (composition) is kinda in the way and prevent me from
thinking about quick solution to implements things.
Movements, actions and physics are a complete mess and split apart.

So far, I find that level generation and autolayout are pretty useful as I can
change tiles easily