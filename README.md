# Webfishing to Midi
Hello all I built this as a way to play the guitar using a midi controller that was with as little limitations as possible. There are currently two known midi controllers to webfishing players I know of:

1. [WEBFISHING Midi Input](https://github.com/Grinjr/WEBFISHING-Midi-Input): This is the one I used before but it would only use the green bar chord buttons to play each individual note. This would make regular chords very hard to play. I use a similar approach to this.
2. [Fishing Potato Midi](https://github.com/ThePotato97/FishingPotatoMidi): This midi player uses GDWeave to play the notes. My anti virus did not trust it in the slightest and neither do I.

So because of that I built this one to fix the issues of the first midi controller. This midi controller does the following:
- Each note is played individually 
- Notes greedily takes strings. Each string has its own cooldown so that notes do not overwrite previous notes where possible.
- It is now built in python so that it is more extendable. Maybe in the future we can have an auto guitar recognition.
- Does not use GDWeave

## To Use: 
1.  Run the `webfishing-midi-player.exe` file.(or run the python program)
2.  You may see an error pop up initially. Please ignore it(do not close it). The application should still function as expected.
3.  Follow the GIF below to `Ctrl+Shift+Click` on the indicated spots in the correct order. Basically you should click on the two corners of the guitar.

![](documentation\proper_bb_select.gif)



## To Build the Binary:
```
pyinstaller webfishing-midi-player.spec
```