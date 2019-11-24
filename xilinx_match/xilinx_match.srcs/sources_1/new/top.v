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
   output pwm1,         //���1
   output pwm2,         //���2
   output pwm3,         //���3
   output pwm4,         //���4
   output pwm5,         //���5
   output pwm6,         //���6
   output pwm7,        //�Ĵ�����������1
   output pwm8,        //�Ĵ�����������2
   output pwm9,        //����ͷ�������1
   output pwm10,       //����ͷ�������2
   output IN1,
   output IN2,
   output IN3,
   output IN4,
   output led_open_closed,
   output [3:0] ledx
);
wire clk_out2;
wire bps_start1,bps_start2;
wire clk_bps1,clk_bps2;//�ߵ�ƽ������
wire [7:0] rx_data;   //�������ݴ洢��,�����洢���յ�������,ֱ����һ�����ݽ���
wire rx_inter;     //���������ж��ź�,���չ�����һֱΪ��
wire [7:0] smoke_state;
wire [7:0] pressure_state;
wire [7:0] temperature;
wire [7:0] humidity;
wire sample_en;

clk_50M clk(         //125MHZת50MHZģ��
       .clk_in1(clk_125M),
       .reset(rst),
       .clk_out1(clk_out2)
);   

 pwm_control control(     //pwm����ģ��
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
 
 uart_rx rx(            //���ݽ���ģ��
     .clk(clk_out2),   //ʱ��
     .rst_n(rest),  //��λ
     .rs232_rx(rs232_rx), //���������ź�
     .clk_bps(clk_bps1),  //�ߵ�ƽʱΪ�����ź��м������
     .bps_start(bps_start1), //�����ź�ʱ,������ʱ���ź���λ
     .rx_data(rx_data),//�������ݼĴ���
     .rx_int(rx_inter),  //���������ж��ź�,���չ�����Ϊ��
     .led(ledx)
 );
 
 uart_tx tx(
    .clk(clk_out2),
    .rst_n(rest),
    .clk_bps(clk_bps2),//�м������
    .rx_data1(smoke_state),//�������ݼĴ���
    .rx_data2(temperature),//�������ݼĴ���
    .rx_data3(humidity),
    .rx_data4(pressure_state),
    .rs232_tx(rs232_tx),//���������ź�
    .bps_start(bps_start2)//�����ź���λ
 );
 
  speed_select speed_rx(
      .clk(clk_out2),       //50Mʱ��
      .rst_n(rest),     //��λ�ź�
      .bps_start(bps_start1), //���յ��ź��Ժ�,������ʱ���ź���λ,�����յ�uart_rx�������ź��Ժ�,ģ�鿪ʼ����
      .clk_bps(clk_bps1)   //���������м������
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