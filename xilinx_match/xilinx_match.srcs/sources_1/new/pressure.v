`timescale 1ns / 1ps

module pressure(
      input clk,
      input rst_n,
      input pressure_rx,
      (* DONT_TOUCH= "TRUE" *)output reg [7:0] pressure_state
    );
    
   reg [7:0] count1;
   reg [7:0] count2;
    
        always @(posedge clk)
   begin
       if(!rst_n) begin
           count1 <= 8'b0;
           count2 <= 8'b0;
       end
       else if(pressure_rx)begin
           count1<=count1+1;
           if(count1 == 8'b0110_0100)begin
           pressure_state <= 8'b0100_0001;    //16进制41
           count1<=8'b0;
           end
       end
       else begin
           count2<=count2+1;
           if(count2 == 8'b0110_0100)begin
           pressure_state <= 8'b0100_0010;    //16进制42
           count2 <= 8'b0;
           end
       end
   end
endmodule
