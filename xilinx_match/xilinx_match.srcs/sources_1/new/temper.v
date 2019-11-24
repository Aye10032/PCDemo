`timescale 1ns / 1ps

module temper(
    input clk,
    input rst_n,
    input sample_en,
    inout data,
    output [7:0] temperature,
    output [7:0] humidity
    );
    reg sample_en_tmp1,sample_en_tmp2;                             
    always @(posedge clk)                                      
    begin                                                                         
       sample_en_tmp1 <=  sample_en;                               
       sample_en_tmp2 <=  sample_en_tmp1;                          
    end                                                        
                                                               
    wire sample_pulse = (~sample_en_tmp2) & sample_en_tmp1;    

    reg data_tmp1,data_tmp2;                                    
    always @(posedge clk)                                     
    begin                                                     
       data_tmp1 <=  data;                                      
       data_tmp2 <=  data_tmp1;                                 
    end                                                       
                                                              
    wire data_pulse = (~data_tmp2) & data_tmp1;
    
    (* DONT_TOUCH= "TRUE" *)reg [3:0] state = 0;
    reg [26:0] power_up_cnt = 0;
    
    reg [20:0] wait_18ms_cnt = 0;
    reg [11:0] wait_40us_cnt = 0;
    
    (* DONT_TOUCH= "TRUE" *)reg [39:0] get_data;
    (* DONT_TOUCH= "TRUE" *)reg [39:0] rx_data;
    reg [5:0] num = 6'd0;
    reg data_reg = 1;
    reg link = 0;
    always @(posedge clk)               
    begin 
       if(!rst_n)begin
           state <= 0;
       end   
                               
       case(state)                      
         0  :  begin
                 link <= 1;
                 data_reg <= 1;//���߿���ʱΪ�ߵ�ƽ
                 power_up_cnt <= power_up_cnt + 1;
                 if(power_up_cnt[26])      //�ȴ�1s����ʱ��
                  begin
                     power_up_cnt <= 0;
                     state <= 1;
                  end
               end                   
         1  :  begin               
                  if(sample_pulse) //����ת������    
                     begin
                        wait_18ms_cnt <= 0;
                        link <= 1;
                        data_reg <= 0; //������������18ms����
                        state <= 2; 
                      end
                end
         2  :  begin                                                             
                  wait_18ms_cnt <= wait_18ms_cnt + 1;
                    if(wait_18ms_cnt[20])
                       begin
                         wait_18ms_cnt <= 0;
                         wait_40us_cnt <= 0;
                         link <= 1;    
                         data_reg <= 1;
                         state <= 3; 
                       end 
                   end      
         3  :  begin                                           
                  wait_40us_cnt <= wait_40us_cnt + 1;  
                    if(wait_40us_cnt[11]) //��ʱ�ȴ�40us  
                      begin                 
                        wait_40us_cnt <= 0; 
                        state <= 4; 
                        link <= 0;
                      end
               end  
         4  :  begin                                                           
                  if(data_pulse) 
                     begin                                    
                       get_data <= 40'd0;
                       num <= 0;
                       state <= 5;                           
                     end                                      
               end                                           
         5  :  begin                                    
                   if(data_pulse)   //��һλ�����е������أ���ʱ40us�����Ϊ����Ϊ0������Ϊ1                   
                      begin          //��Ϊ0��Ӧ�ĸߵ�ƽʱ��26us��1��Ӧ�ĸߵ�ƽʱ��70us                     
                        wait_40us_cnt <= 0;
                        state <= 6;                      
                       end                                 
               end
         6  :  begin                                                                          
                  wait_40us_cnt <= wait_40us_cnt + 1;     
                   if(wait_40us_cnt[11]) //��ʱ�ȴ�40us    
                     begin
                       wait_40us_cnt <= 0;
                       num <= num + 1;
                       if(data)
                          rx_data[num] <= 1'b1;
//                           get_data <= {get_data[38:0],1'b1};                          
                       else
                          rx_data[num] <= 1'b0;
//                           get_data <= {get_data[38:0],1'b0}; 
                       if(num == 6'd39)
                           begin
                               num <= 0;
                               state <= 1;  
                               get_data <= rx_data;
                           end
                       else
                               state <= 5;                                   
                     end      
                end
         default:  state <= 0; 
       endcase       
    end 
    
    assign data  = link ? data_reg : 1'bz;
    assign humidity = get_data[7:0];
    assign temperature = get_data[23:16];
   
  
endmodule
