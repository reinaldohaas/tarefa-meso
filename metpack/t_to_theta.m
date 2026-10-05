 function [theta] = t_to_theta(t,p)
% t_to_theta generates theta from T (degC) p(mb) vectors
% output [theta] = t_to_theta(t,p)

% changed rsat denominator from p to p-es - 3 may 07
%convert t,p to SI units
 tk = t + 273.15; %K
 p = p*100; %Pa

%calculate the potential temperature from temperature array
 p0=1000*100;	%reference pressure Pa
 R=287;		%gas constant
 cp=1004;	%specific heat wrt pressure
 K= R/cp;
 a = real((p/p0).^(-K));
 theta = tk.*a;











