`timescale 1ns / 1ps

module smoke(
    input clk,
    input rst_n,
    input smoke_rx,
    (* DONT_TOUCH= "TRUE" *)output reg [7:0] smoke_state
//    output[3:0] led
    );
    
//    reg [3:0] ledx;
    reg [7:0] count1;
    reg [7:0] count2;


    always @(posedge clk)
    begin
        if(!rst_n) begin
            count1 <= 8'b0;
            count2 <= 8'b0;
        end
        else if(smoke_rx)begin
            count1<=count1+1;
            if(count1 == 8'b0110_0100)begin
            smoke_state <= 8'b0011_0001;    //16进制31
            count1<=8'b0;
//            ledx[0]<=1;
            end
        end
        else begin
            count2<=count2+1;
            if(count2 == 8'b0110_0100)begin
            smoke_state <= 8'b0011_0010;    //16进制32
            count2 <= 8'b0;
//            ledx[0]<=0;
            end
        end
    end
    
//    assign led = ledx;
    
endmodule
