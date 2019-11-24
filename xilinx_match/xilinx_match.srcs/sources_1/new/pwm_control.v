`timescale 1ns / 1ps

module pwm_control(
    input clk,
    input rst_n,
    input [7:0] rx_data,    //接收数据寄存器
    input rx_int,           //数据接收中断信号
    output reg pwm1,        //机械臂舵机1
    output reg pwm2,        //机械臂舵机2
    output reg pwm3,        //机械臂舵机3
    output reg pwm4,        //机械臂舵机4
    output reg pwm5,        //机械臂舵机5
    output reg pwm6,        //机械臂舵机6
    output reg pwm7,        //履带车变速驱动1
    output reg pwm8,        //履带车变速驱动2
    output reg pwm9,        //摄像头舵机控制1
    output reg pwm10,       //摄像头舵机控制2
    output reg IN1,
    output reg IN2,
    output reg IN3,
    output reg IN4,
    output reg led_open_closed
    );
    
    reg [19:0] count_for_pwmclk = 0;  //pwm_clk的累加器
    reg pwm_clk=0;                  //pwm_clk的信号
     (* DONT_TOUCH= "TRUE" *)reg [7:0] store_data;    //用来暂时存放数据内容

    reg [11:0] count_pwm1=0; 
    reg [11:0] count_pwm2=0; 
    reg [11:0] count_pwm3=0; 
    reg [11:0] count_pwm4=0; 
    reg [11:0] count_pwm5=0; 
    reg [11:0] count_pwm6=0; 
    reg [11:0] count_pwm7=0; 
    reg [11:0] count_pwm8=0; 
    reg [11:0] count_pwm9=0;
    reg [11:0] count_pwm10=0;

     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare1 = 12'b0000_1001_0110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare2 = 12'b0000_1001_0110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare3 = 12'b0000_1001_0010;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare4 = 12'b0000_1000_1111;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare5 = 12'b0000_1011_0110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare6 = 12'b0000_1010_0101;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare7 = 12'b0000_0001_1110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare8 = 12'b0000_0001_1110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare9 = 12'b0000_1001_0110;
     (* DONT_TOUCH= "TRUE" *)reg [11:0] pwm_compare10 = 12'b0000_1001_0110;
     
    
     (* DONT_TOUCH= "TRUE" *) reg rx_int0,rx_int1,rx_int2;//信号寄存器,捕捉下降沿
     wire neg_rx_int;    //下降沿标志
     
     always @(posedge clk) begin
          if(!rst_n) begin
           rx_int0 <= 1'b0;
           rx_int1 <= 1'b0;
           rx_int2 <= 1'b0;
          end
          else begin
            rx_int0 <= rx_int;
            rx_int1 <= rx_int0;
            rx_int2 <= rx_int1;
          end
      end
         
     assign neg_rx_int = ~rx_int1 & rx_int2;//捕捉下沿
 
     always @(posedge clk)
        begin
            if(!rst_n)begin
               store_data <= 8'd0;
               pwm_compare1 <= 12'b0000_1001_0110;//1.5ms
               pwm_compare2 <= 12'b0000_1001_0110;//1.5ms
               pwm_compare3 <= 12'b0000_1001_0010;//1.46ms
               pwm_compare4 <= 12'b0000_1000_1111;//1.43ms
               pwm_compare5 <= 12'b0000_1011_0110;//1.82ms
               pwm_compare6 <= 12'b0000_1010_0101;//1.65ms
               
               pwm_compare7 <= 12'b0000_0001_1110;//30us
               pwm_compare8 <= 12'b0000_0001_1110;//30us
               
               pwm_compare9 <= 12'b0000_1001_0110;//1.5ms
               pwm_compare10 <= 12'b0000_1001_0110;//1.5ms

            end
            
            if(neg_rx_int) begin
               store_data <= rx_data;
              end
               case(store_data)
              8'h32: begin pwm_compare1<=pwm_compare1+12'b0000_0000_0010; if(pwm_compare1>=12'b0000_1010_0000) pwm_compare1 <= 12'b0000_1010_0000;store_data<=8'd0;end   //pwm1
              8'h31: begin pwm_compare1<=pwm_compare1-12'b0000_0000_0010; if(pwm_compare1<=12'b0000_0101_0110) pwm_compare1 <= 12'b0000_0101_0110;store_data<=8'd0; end
              
              8'h33: begin pwm_compare2<=pwm_compare2+12'b0000_0000_0010; if(pwm_compare2>=12'b0000_1111_0000) pwm_compare2 <= 12'b0000_1111_0000;store_data<=8'd0;end   //pwm2
              8'h34: begin pwm_compare2<=pwm_compare2-12'b0000_0000_0010; if(pwm_compare2<=12'b0000_0011_1100) pwm_compare2 <= 12'b0000_0011_1100;store_data<=8'd0; end
              
              8'h35: begin pwm_compare3<=pwm_compare3+12'b0000_0000_0010; if(pwm_compare3>=12'b0000_1111_0000) pwm_compare3 <= 12'b0000_1111_0000;store_data<=8'd0; end   //pwm3
              8'h36: begin pwm_compare3<=pwm_compare3-12'b0000_0000_0010; if(pwm_compare3<=12'b0000_0011_1100) pwm_compare3 <= 12'b0000_0011_1100;store_data<=8'd0; end
              
//              8'h37: begin pwm_compare4<=pwm_compare4+12'b0000_0000_0101; if(pwm_compare4>=12'b0000_1111_0000) pwm_compare4 <= 12'b0000_1111_0000;store_data<=8'd0;  end   //pwm4
//              8'h38: begin pwm_compare4<=pwm_compare4-12'b0000_0000_0101; if(pwm_compare4<=12'b0000_0011_1100) pwm_compare4 <= 12'b0000_0011_1100;store_data<=8'd0;  end
              
//              8'h39: begin pwm_compare5<=pwm_compare5+12'b0000_0000_0101; if(pwm_compare5>=12'b0000_1011_0110) pwm_compare5 <= 12'b0000_1011_0110;store_data<=8'd0;  end   //pwm5
//              8'h40: begin pwm_compare5<=pwm_compare5-12'b0000_0000_0101; if(pwm_compare5<=12'b0000_0011_1100) pwm_compare5 <= 12'b0000_0011_1100;store_data<=8'd0;  end

              8'h37: begin pwm_compare4<=pwm_compare4+12'b0000_0000_0101; if(pwm_compare5>=12'b0000_1011_0110) pwm_compare4 <= 12'b0000_1000_1111;
                           pwm_compare5<=pwm_compare5+12'b0000_0000_0101; if(pwm_compare5>=12'b0000_1011_0110) pwm_compare5 <= 12'b0000_1011_0110; store_data<=8'd0; end  
              8'h38: begin pwm_compare4<=pwm_compare4-12'b0000_0000_0101;if(pwm_compare4<=12'b0000_0011_1100) pwm_compare4 <= 12'b0000_0011_1100; 
                           pwm_compare5<=pwm_compare5-12'b0000_0000_0101;if(pwm_compare5<=12'b0000_0011_1100) pwm_compare5 <= 12'b0000_0011_1100;  store_data<=8'd0; end

              8'h41: begin pwm_compare6<=pwm_compare6+12'b0000_0000_0010; if(pwm_compare6>=12'b0000_1100_0111) pwm_compare6 <= 12'b0000_1100_0111;store_data<=8'd0; end   //pwm6
              8'h42: begin pwm_compare6<=pwm_compare6-12'b0000_0000_0010; if(pwm_compare6<=12'b0000_1000_0011) pwm_compare6 <= 12'b0000_1000_0011;store_data<=8'd0; end
              
              8'h43:begin IN1<=1; IN2<=0; IN3<=0; IN4<=1; store_data<=8'd0; end     //前进
              8'h44:begin IN1<=0; IN2<=1; IN3<=1; IN4<=0; store_data<=8'd0; end     //后退
              8'h45:begin IN1<=1; IN2<=0; IN3<=1; IN4<=0; store_data<=8'd0; end     //右转
              8'h46:begin IN1<=0; IN2<=1; IN3<=0; IN4<=1; store_data<=8'd0; end     //左转
              8'h47:begin IN1<=0; IN2<=0; IN3<=0; IN4<=0; store_data<=8'd0; end     //停止
              8'h48:begin  pwm_compare7 <= 12'b0000_0011_0010;pwm_compare8 <= 12'b0000_0011_0010;  store_data<=8'd0; end  //占空比百分之50    
              8'h49:begin  pwm_compare7 <= 12'b0000_0001_1110;pwm_compare8 <= 12'b0000_0001_1110;  store_data<=8'd0; end  //占空比百分之30
              8'h52:begin  pwm_compare7 <= 12'b0000_0001_0100;pwm_compare8 <= 12'b0000_0001_0100;  store_data<=8'd0; end  //占空比百分之20
              8'h50:begin  led_open_closed<=1;  store_data<=8'd0; end       //车灯打开
              8'h51:begin  led_open_closed<=0;  store_data<=8'd0;end        //车灯关闭
              
              8'h53:begin  pwm_compare9<=pwm_compare9+12'b0000_0000_0010;if(pwm_compare9>=12'b0000_1010_1010) pwm_compare9 <= 12'b0000_1010_1010;store_data<=8'd0; end      //pwm9
              8'h54:begin  pwm_compare9<=pwm_compare9-12'b0000_0000_0010; if(pwm_compare9<=12'b0000_1000_0010) pwm_compare9 <= 12'b0000_1000_0010;store_data<=8'd0; end
              
              8'h55:begin  pwm_compare10<=pwm_compare10+12'b0000_0000_0010;if(pwm_compare10>=12'b0000_1010_1110) pwm_compare10 <= 12'b0000_1010_1110;store_data<=8'd0; end  //pwm10
              8'h56:begin  pwm_compare10<=pwm_compare10-12'b0000_0000_0010; if(pwm_compare10<=12'b0000_1000_0100) pwm_compare10 <= 12'b0000_1000_0100;store_data<=8'd0; end
  
               default:;
        endcase
      end
     
      
      always @(posedge clk)   //clk是50Mhz的时钟信号
         begin
              if(count_for_pwmclk == 20'b0000_0000_0000_1111_1010-1) begin    // 0.01ms触发一次，故pwm波形精度为0.01ms 
                 count_for_pwmclk <= 0;
                 pwm_clk <= ~pwm_clk;   //按位取反
               end
              else
                 count_for_pwmclk <= count_for_pwmclk + 1;
         end

         always @(posedge pwm_clk)    //控制pwm1信号输出
            begin
                count_pwm1<=count_pwm1+1;
                if (count_pwm1 < pwm_compare1)   
                      pwm1 <= 1;
                else
                      pwm1 <= 0;
                if (count_pwm1 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                begin
                    count_pwm1<=0;
                    
                end   
             end 
             
         always @(posedge pwm_clk)    //控制pwm2信号输出
              begin
                count_pwm2<=count_pwm2+1;
                if (count_pwm2 < pwm_compare2)   
                    pwm2<=1;
                else
                    pwm2<=0;
                if (count_pwm2 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                    count_pwm2<=0;
             end              
             
         always @(posedge pwm_clk)    //控制pwm3信号输出
              begin
                count_pwm3<=count_pwm3+1;
               if (count_pwm3 < pwm_compare3)   
                   pwm3<=1;
               else
                   pwm3<=0;
               if (count_pwm3 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                   count_pwm3<=0;
             end              
             
          always @(posedge pwm_clk)    //控制pwm4信号输出
              begin
                count_pwm4<=count_pwm4+1;
              if (count_pwm4 < pwm_compare4)   
                    pwm4<=1;
              else
                    pwm4<=0;
              if (count_pwm4 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                   count_pwm4<=0;
              end             
             
         always @(posedge pwm_clk)    //控制pwm5信号输出
             begin
                count_pwm5<=count_pwm5+1;
              if (count_pwm5 < pwm_compare5)   
                    pwm5<=1;
              else
                    pwm5<=0;
              if (count_pwm5 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                    count_pwm5<=0;
             end              
             
          always @(posedge pwm_clk)    //控制pwm6信号输出
             begin
                count_pwm6<=count_pwm6+1;
             if (count_pwm6 < pwm_compare6)  
                    pwm6<=1;
             else
                    pwm6<=0;
             if (count_pwm6 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                    count_pwm6<=0;
             end             
             
          always @(posedge pwm_clk)    //控制pwm7信号输出
               begin
                 count_pwm7<=count_pwm7+1;
               if (count_pwm7 < pwm_compare7)   //pwm7
                   pwm7<=1;
               else
                   pwm7<=0;
               if (count_pwm7 ==12'b0000_0110_0100-1)  //每0.01ms加一次，加100次,周期为1ms,1kHZ
                   count_pwm7<=0;
             end              
             
           always @(posedge pwm_clk)    //控制pwm8信号输出
               begin
                 count_pwm8<=count_pwm8+1;
               if (count_pwm8 < pwm_compare8)   //pwm8
                   pwm8<=1;
               else
                   pwm8<=0;
               if (count_pwm8 ==12'b0000_0110_0100-1)  //每0.01ms加一次，加100次,周期为1ms,1kHZ
                   count_pwm8<=0;
             end     
             
           always @(posedge pwm_clk)    //控制pwm9信号输出
                begin
                   count_pwm9<=count_pwm9+1;
                if (count_pwm9 < pwm_compare9)  
                       pwm9<=1;
                else
                       pwm9<=0;
                if (count_pwm9 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                       count_pwm9<=0;
                end 
                
            always @(posedge pwm_clk)    //控制pwm10信号输出
                 begin
                    count_pwm10<=count_pwm10+1;
                 if (count_pwm10 < pwm_compare10)  
                       pwm10<=1;
                 else
                       pwm10<=0;
                 if (count_pwm10 ==12'b0111_1101_0000-1)  //每0.01ms加一次，加2000次即为20ms的周期
                       count_pwm10<=0;
                 end 
            
endmodule
