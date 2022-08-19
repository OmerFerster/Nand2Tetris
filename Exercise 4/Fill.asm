// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
    @KBD  // checks if KeyBoard got input
    D = M
    @i
    M = 0;
    @WHITE
    D;JEQ  // Jumps to ALL WHITE SCREEN if non-key pressed
    ////////////////////////////////////////////
    (BLACK)  // Apply A full black SCREEN beacuse something is being pressed
        @i
        D = M
        @8191
        D = A - D // checks if 8191 - i >= 0 --> not done painting
        @BLOOP
        D;JGE
        @LOOP
        0;JMP
        (BLOOP)
            @i
            D = M
            @SCREEN
            A = A + D
            M = -1
            @i
            M = M + 1
            @BLACK
            0;JMP
    ////////////////////////////////////////////
    (WHITE)  // Apply A full white SCREEN beacuse nothing pressed
        @i
        D = M
        @8191
        D = A - D  // checks if 8191 - i >= 0 --> not done painting
        @WLOOP
        D;JGE
        @LOOP
        0;JMP
        (WLOOP)
           @i
           D = M
           @SCREEN
           A = A + D
           M = 0
           @i
           M = M + 1
           @WHITE
           0;JMP