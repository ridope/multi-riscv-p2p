// -----------------------------------------------------------------------------
// Auto-Generated by:        __   _ __      _  __
//                          / /  (_) /____ | |/_/
//                         / /__/ / __/ -_)>  <
//                        /____/_/\__/\__/_/|_|
//                     Build your hardware, easily!
//                   https://github.com/enjoy-digital/litex
//
// Filename   : top.v
// Device     : 10M50DAF484C7G
// LiteX sha1 : 3fde2512
// Date       : 2022-02-09 16:18:11
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// Module
//------------------------------------------------------------------------------

module top (
	output wire user_led0,
	output wire user_led1,
	output wire user_led2,
	output wire user_led3,
	input  wire user_sw0,
	input  wire user_sw1,
	input  wire user_sw2,
	input  wire user_sw3,
	input  wire clk50
);


//------------------------------------------------------------------------------
// Signals
//------------------------------------------------------------------------------

wire sys_clk;
wire sys_rst;
wire por_clk;
reg  int_rst = 1'd1;

//------------------------------------------------------------------------------
// Combinatorial Logic
//------------------------------------------------------------------------------

assign user_led0 = (user_sw0 | user_sw1);
assign user_led1 = (~(user_sw0 | user_sw1));
assign user_led2 = (user_sw2 & user_sw3);
assign user_led3 = (~(user_sw2 & user_sw3));
assign sys_clk = clk50;
assign por_clk = clk50;
assign sys_rst = int_rst;


//------------------------------------------------------------------------------
// Synchronous Logic
//------------------------------------------------------------------------------

always @(posedge por_clk) begin
	int_rst <= 1'd0;
end

always @(posedge sys_clk) begin
	if (sys_rst) begin
	end
end


//------------------------------------------------------------------------------
// Specialized Logic
//------------------------------------------------------------------------------

endmodule

// -----------------------------------------------------------------------------
//  Auto-Generated by LiteX on 2022-02-09 16:18:11.
//------------------------------------------------------------------------------
