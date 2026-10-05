 function [nsq, nsqe] = brunt_p(theta, thetae, p) 
%use [nsq, nsqe] = brunt_p(theta, thetae, p)
 % brunt_p calculates the brunt-vaisalla frequency for theta and thetae
% using p as a vertical coordinate, theta, thetae in K, p (mb)

p = p*100; %change to Pa

%set up constants
 p0=1000*100;	%reference pressure Pa
 R=287;		%gas constant
 g=9.8;
 theta0=273.15;
 cp=1004;	%specific heat wrt pressure
 K= R/cp;
 alpha = g*g/(R*theta0);
 a = ((p./p0).^(K));
 t = theta.*a;

%calculate dtheta/dp using forward differencing
 dtheta = diff(theta);
 dp = diff(p);
 dtheta(length(theta)) =  dtheta(length(theta)-1);
 dp(length(p)) =  dp(length(p)-1);
 nsq = -alpha*p.*dtheta./t.*dp;

%calculate dthetae/dp using forward differencing
 dthetae = diff(thetae);
 dthetae(length(thetae)) =  dthetae(length(thetae)-1);
 nsqe = -alpha*p.*dthetae./t.*dp;


