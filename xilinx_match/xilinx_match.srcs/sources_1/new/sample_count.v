`timescale 1ns / 1ps

module sample_count(
        input clk,
        output reg sample_en
    );
    reg [3:0] state = 0;
    reg [27:0] power_up_cnt = 0; 
    
    always @(posedge clk)               
    begin                               
       case(state)                      
         0  :  begin
                  power_up_cnt <= power_up_cnt + 1;
                  if(power_up_cnt[26])      //等待1s左右时间      
                    begin
                       power_up_cnt <= 0;
                       state <= 1;
                    end
                 end
          1  :   begin
                    sample_en <= 0;
                    power_up_cnt <= power_up_cnt + 1;
                      if(power_up_cnt[26])      //每隔1s采集一次温、湿度  
                        begin
                          power_up_cnt <= 0;
                          sample_en <= 1;
                        end
                        else
                           state <= 1;
                  end
          default:  state <= 0;    
       endcase       
    end     
    
endmodule
