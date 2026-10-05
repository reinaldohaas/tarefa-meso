function success=theta_thetae(z,theta,thetae)
%Use success=theta_thetae(z,theta,thetae)

plot(theta,z);
hold on
plot(thetae,z,'r');

grid on
xlabel('Theta and Thetae in Kelvins'), ylabel ('height  km');
title('potential temperature and potential equivalente temperature'),xlabel('(K)'), ylabel('height km')
% 
xlabel('Temperature (C)','fontweight','bold')
ylabel('Altitude (m)','fontweight','bold')
success='yes';
