`timescale 1ns / 1ps

module top(
   input clk_125M, 
   input rst,
   input rest,
   input rs232_rx,
   input smoke_rx,
   input pressure_rx,
   inout data,
   output rs232_tx,
   output pwm1,         //舵机1
   output pwm2,         //舵机2
   output pwm3,         //舵机3
   output pwm4,         //舵机4
   output pwm5,         //舵机5
   output pwm6,         //舵机6
   output pwm7,        //履带车变速驱动1
   output pwm8,        //履带车变速驱动2
   output pwm9,        //摄像头舵机控制1
   output pwm10,       //摄像头舵机控制2
   output IN1,
   output IN2,
   output IN3,
   output IN4,
   output led_open_closed,
   output [3:0] ledx
);
wire clk_out2;
wire bps_start1,bps_start2;
wire clk_bps1,clk_bps2;//高电平采样点
wire [7:0] rx_data;   //接收数据存储器,用来存储接收到的数据,直到下一个数据接收
wire rx_inter;     //接收数据中断信号,接收过程中一直为高
wire [7:0] smoke_state;
wire [7:0] pressure_state;
wire [7:0] temperature;
wire [7:0] humidity;
wire sample_en;

clk_50M clk(         //125MHZ转50MHZ模块
       .clk_in1(clk_125M),
       .reset(rst),
       .clk_out1(clk_out2)
);   

 pwm_control control(     //pwm控制模块
      .clk(clk_out2),
      .rst_n(rest),
      .rx_data(rx_data),
      .rx_int(rx_inter),
      .pwm1(pwm1),
      .pwm2(pwm2),
      .pwm3(pwm3),
      .pwm4(pwm4),
      .pwm5(pwm5),
      .pwm6(pwm6),
      .pwm7(pwm7),      
      .pwm8(pwm8),     
      .pwm9(pwm9),
      .pwm10(pwm10),   
      .IN1(IN1),
      .IN2(IN2),
      .IN3(IN3),
      .IN4(IN4),
      .led_open_closed(led_open_closed)
 );
 
 uart_rx rx(            //数据接收模块
     .clk(clk_out2),   //时钟
     .rst_n(rest),  //复位
     .rs232_rx(rs232_rx), //接收数据信号
     .clk_bps(clk_bps1),  //高电平时为接收信号中间采样点
     .bps_start(bps_start1), //接收信号时,波特率时钟信号置位
     .rx_data(rx_data),//接收数据寄存器
     .rx_int(rx_inter),  //接收数据中断信号,接收过程中为高
     .led(ledx)
 );
 
 uart_tx tx(
    .clk(clk_out2),
    .rst_n(rest),
    .clk_bps(clk_bps2),//中间采样点
    .rx_data1(smoke_state),//接收数据寄存器
    .rx_data2(temperature),//接收数据寄存器
    .rx_data3(humidity),
    .rx_data4(pressure_state),
    .rs232_tx(rs232_tx),//发送数据信号
    .bps_start(bps_start2)//发送信号置位
 );
 
  speed_select speed_rx(
      .clk(clk_out2),       //50M时钟
      .rst_n(rest),     //复位信号
      .bps_start(bps_start1), //接收到信号以后,波特率时钟信号置位,当接收到uart_rx传来的信号以后,模块开始运行
      .clk_bps(clk_bps1)   //接收数据中间采样点
  );
  
    speed_select speed_tx(
      .clk(clk_out2),      
      .rst_n(rest),     
      .bps_start(bps_start2), 
      .clk_bps(clk_bps2)   
  );

    smoke sm_rx(
      .clk(clk_out2),
      .rst_n(rest), 
      .smoke_rx(smoke_rx),
      .smoke_state(smoke_state)
//      .led(ledx)
    );
    
     pressure pr_rx(
      .clk(clk_out2),
      .rst_n(rest), 
      .pressure_rx(pressure_rx),
      .pressure_state(pressure_state)
    );
    
    temper temp(
     .clk(clk_out2),
     .rst_n(rest),
     .sample_en(sample_en),
     .data(data),
     .temperature(temperature),
     .humidity(humidity)
    );
    
    sample_count count(
     .clk(clk_out2),
     .sample_en(sample_en)
    );

endmodule