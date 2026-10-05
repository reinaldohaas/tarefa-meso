 function [t] = theta_to_t(theta,p)
% theta_to_t generates t (K) from theta (K) and p(mb) vectors
% function [t] = theta_to_t(theta,p)

%convert p to SI units
 p = p*100; %Pa

%calculate the potential temperature from temperature array
 p0=1000*100;	%reference pressure Pa
 R=287;		%gas constant
 cp=1004;	%specific heat wrt pressure
 K= R/cp;
 a = ((p./p0).^(-K));
 t = theta./a;









