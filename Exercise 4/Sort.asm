// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

@i
M = 1
@R15
D = M - 1
@END  // END if arr length is less than 1 means that arr is already sorted
D;JLE
 ////////////////////////////////////////
(FIRSTLOOP)
    @j
    M = 0
     ////////////////////////////////////////
    (SECONDLOOP)
        @j
        D = M
        @R15
        D = M - D
        @INCI
        D;JEQ  // checks if specific iteration is over
        @j
        D = M
        @R14
        D = D + M
        A = D
        D = M
        @first  // variable that save arr[j]
        M = D
        @j              
        M = M + 1
        D = M
        @R14
        D = D + M
        A = D
        D = M
        @second  // variable that save arr[j + 1] 
        M = D
        D = M
        @first
        D = D - M  // D saves the result of arr[j+1] - arr[j]
        @SWAP  // if arr[j+1] > arr[j] SWAP them
        D;JGT
        @SECONDLOOP
        0;JMP
        ////////////////////////////////////////
        (SWAP)  //  swapping process
            @R14
            D = M
            @j
            D = D + M
            @temp
            M = D
            @first
            D = M
            @temp
            A = M
            M = D
            @R14
            D = M
            @j
            D = D + M
            D = D - 1
            @temp
            M = D
            @second
            D = M
            @temp
            A = M
            M = D 
            @SECONDLOOP
            0;JMP
     ////////////////////////////////////////
    (INCI)  // next iteration process
        @i
        M = M + 1
        D = M
        @R15
        D = M - D
        @END
        D;JLT
        @FIRSTLOOP
        0;JMP
 ////////////////////////////////////////     
(END)  // infinite loop
    @END
    0;JMP
