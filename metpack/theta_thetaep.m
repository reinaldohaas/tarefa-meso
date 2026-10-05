function success=theta_thetae_p(p,theta,thetae)
%Use success=theta_thetaep(p,theta,thetae)
axis ij
plot(theta,p);
hold on
plot(thetae,p,'r');
axis([280 600 0 1000 ])
%inverte o eixos para plotar pressão
axis ij
grid on
xlabel('Theta and Thetae in Kelvins'), ylabel ('Pressure  hPa');
title('potential temperature and potential equivalente temperature'),xlabel('(K)'), ylabel('height km')
% 
xlabel('Temperature (C)','fontweight','bold')
ylabel('Pressure (hPa)','fontweight','bold')
success='yes';
