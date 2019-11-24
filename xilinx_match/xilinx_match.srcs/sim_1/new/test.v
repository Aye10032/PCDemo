`timescale 1ns / 1ps

module test();
parameter CLKPERIOD=13020;
    reg clk;
    reg rst;
    reg rest;
    reg rx;
    wire tx;
    wire pwm_out;
    wire[3:0] led;
    wire N;

always #4 clk=~clk;

initial 
    begin
        # 50 rst<=1;
        #100 rst<=0;
        # 50 rest<=0;
        #100 rest<=1;
         clk<=0;
          #(CLKPERIOD*49) rx = 0;
          #(CLKPERIOD*8) rx = 0;
          #(CLKPERIOD*8) rx = 1;
          #(CLKPERIOD*8) rx = 1;
          #(CLKPERIOD*8) rx = 0;
          #(CLKPERIOD*8) rx = 0;
          #(CLKPERIOD*8) rx = 0;
          #(CLKPERIOD*8) rx = 1;
          #(CLKPERIOD*8) rx = 0;
          #(CLKPERIOD*8) rx = 0;
    end
    
    top istest(
        .clk_125M(clk),
        .rst(rst),
        .rest(rest),
        .rs232_rx(rx),
        .rs232_tx(tx),
        .pwm(pwm_out),
        .ledx(led),
        .N(N)
    );

endmodule
