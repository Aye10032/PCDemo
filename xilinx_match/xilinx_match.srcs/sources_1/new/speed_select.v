`timescale 1ns / 1ps

module speed_select(
    input clk,       //50Mʱ��
    input rst_n,     //��λ�ź�
    input bps_start, //���յ��ź��Ժ�,������ʱ���ź���λ,�����յ�uart_rx�������ź��Ժ�,ģ�鿪ʼ����
    output clk_bps   //���������м������
    );
    
    reg[24:0] cnt;//��Ƶ������
    reg clk_bps_r;//������ʱ�ӼĴ���
    reg[2:0] uart_ctrl;//������ѡ��Ĵ���
   
    always @(posedge clk)
     if(!rst_n)
      cnt<=13'd0;
     else if((cnt==5208)|| !bps_start)//�жϼ����Ƿ�ﵽ1������
      cnt<=13'd0;
     else
      cnt<=cnt+1'b1;//������ʱ������
   
    always @(posedge clk) begin
     if(!rst_n)
      clk_bps_r<=1'b0;
     else if(cnt== 2604)//�������ʼ�����һ��ʱ,���в����洢
      clk_bps_r<=1'b1;
     else
      clk_bps_r<=1'b0;
    end
    assign clk_bps = clk_bps_r;//���������������uart_rxģ��
   endmodule
