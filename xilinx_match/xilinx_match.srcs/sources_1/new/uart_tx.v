`timescale 1ns / 1ps

module uart_tx(
    input clk,
    input rst_n,
    input clk_bps,//中间采样点
    (* DONT_TOUCH= "TRUE" *)input [7:0] rx_data1,//接收数据寄存器1   烟雾
    (* DONT_TOUCH= "TRUE" *)input [7:0] rx_data2,//接收数据寄存器2   温度
    (* DONT_TOUCH= "TRUE" *)input [7:0] rx_data3,//接收数据寄存器3   湿度
    (* DONT_TOUCH= "TRUE" *)input [7:0] rx_data4,//接收数据寄存器4   压力
    output rs232_tx,//发送数据信号
    output bps_start//发送信号置位
    );
    
    (* DONT_TOUCH= "TRUE" *)reg [7:0] data1;
    (* DONT_TOUCH= "TRUE" *)reg [7:0] data2;
    (* DONT_TOUCH= "TRUE" *)reg [7:0] data3;
    (* DONT_TOUCH= "TRUE" *)reg [7:0] data4;
    
    reg [7:0] tx_data1;//待发送数据1
    reg [7:0] tx_data2;//待发送数据2
    reg [7:0] tx_data3;//待发送数据3
    reg [7:0] tx_data4;//待发送数据4
    reg bps_start_r;
    reg tx_en;//发送信号使能,高有效
    reg [7:0] num;
//    reg [27:0] count1;
    
    always @(posedge clk) begin
//    count1 <= count1 + 1;
      data1 <= rx_data1;
      data2 <= rx_data2;
      data3 <= rx_data3;
      data4 <= rx_data4;
      if(!rst_n) begin
       bps_start_r <= 1'bz;
       tx_en <= 1'b0;
       tx_data1 <= 8'd0;
       tx_data2 <= 8'd0;
       tx_data3 <= 8'b0;
       tx_data4 <= 8'b0;
//       count1 <= 28'b0;
      end
//      else if(count1 == 28'b0010_1111_1010_1111_0000_1000_0000 ) begin   //1秒执行一次
     else begin
       bps_start_r <= 1'b1;
       tx_data1 <= data1;
       tx_data2 <= data2;
       tx_data3 <= data3;
       tx_data4 <= data4;
       tx_en <= 1'b1;
      end
//      else if(num==8'd40) begin
//       bps_start_r <= 1'b0;
//       tx_en <= 1'b0;
//      end 
     end
     
     reg rs232_tx_r;
     always @(posedge clk) begin
      if(!rst_n) begin
       num<=8'd0;
       rs232_tx_r <= 1'b1;
      end
      else if(tx_en) begin
       if(clk_bps) begin
        num<=num+1'b1;
        case(num)
          8'd0: rs232_tx_r <= 1'b0;//起始位
          8'd1: rs232_tx_r <= 1'b1;//数据位 开始
          8'd2: rs232_tx_r <= 1'b1;
          8'd3: rs232_tx_r <= 1'b1;
          8'd4: rs232_tx_r <= 1'b1;
          8'd5: rs232_tx_r <= 1'b1;
          8'd6: rs232_tx_r <= 1'b1;
          8'd7: rs232_tx_r <= 1'b1;
          8'd8: rs232_tx_r <= 1'b1;
          8'd9: rs232_tx_r <= 1'b1;//数据结束位,1位
        
        
        
          8'd10: rs232_tx_r <= 1'b0;//起始位
          8'd11: rs232_tx_r <= tx_data1[0];//数据位 开始
          8'd12: rs232_tx_r <= tx_data1[1];
          8'd13: rs232_tx_r <= tx_data1[2];
          8'd14: rs232_tx_r <= tx_data1[3];
          8'd15: rs232_tx_r <= tx_data1[4];
          8'd16: rs232_tx_r <= tx_data1[5];
          8'd17: rs232_tx_r <= tx_data1[6];
          8'd18: rs232_tx_r <= tx_data1[7];
          8'd19: rs232_tx_r <= 1'b1;//数据结束位,1位
          
          8'd20: rs232_tx_r <= 1'b0;//起始位
          8'd21: rs232_tx_r <= tx_data2[0];//数据位 开始
          8'd22: rs232_tx_r <= tx_data2[1];
          8'd23: rs232_tx_r <= tx_data2[2];
          8'd24: rs232_tx_r <= tx_data2[3];
          8'd25: rs232_tx_r <= tx_data2[4];
          8'd26: rs232_tx_r <= tx_data2[5];
          8'd27: rs232_tx_r <= tx_data2[6];
          8'd28: rs232_tx_r <= tx_data2[7];
          8'd29: rs232_tx_r <= 1'b1;//数据结束位,1位
          
          8'd30: rs232_tx_r <= 1'b0;//起始位
          8'd31: rs232_tx_r <= tx_data3[0];//数据位 开始
          8'd32: rs232_tx_r <= tx_data3[1];
          8'd33: rs232_tx_r <= tx_data3[2];
          8'd34: rs232_tx_r <= tx_data3[3];
          8'd35: rs232_tx_r <= tx_data3[4];
          8'd36: rs232_tx_r <= tx_data3[5];
          8'd37: rs232_tx_r <= tx_data3[6];
          8'd38: rs232_tx_r <= tx_data3[7];
          8'd39: rs232_tx_r <= 1'b1;//数据结束位,1位
          
          8'd40: rs232_tx_r <= 1'b0;//起始位
          8'd41: rs232_tx_r <= tx_data4[0];//数据位 开始
          8'd42: rs232_tx_r <= tx_data4[1];
          8'd43: rs232_tx_r <= tx_data4[2];
          8'd44: rs232_tx_r <= tx_data4[3];
          8'd45: rs232_tx_r <= tx_data4[4];
          8'd46: rs232_tx_r <= tx_data4[5];
          8'd47: rs232_tx_r <= tx_data4[6];
          8'd48: rs232_tx_r <= tx_data4[7];
          8'd49: rs232_tx_r <= 1'b1;//数据结束位,1位
          
          default: rs232_tx_r <= 1'b1;
        endcase
       end
       else if(num==8'd50)
        num<=8'd0;//发送完成,复位
      end
     end
     assign bps_start = bps_start_r;
     assign rs232_tx = rs232_tx_r;
endmodule
