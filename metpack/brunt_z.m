 function [nsq, nsqe] = brunt_z(theta, thetae, z) 
% brunt_z calculates the brunt-vaisalla frequency for theta and thetae
% using z as a vertical coordinate and assuming theta(sonde_no, data)

%set up constants
 g=9.8;
 theta0=273.15;

%calculate dtheta/dz using forward differencing 
 dtheta = diff(theta,1,2); %difference over columns
 dz = diff(z,1,2);
 dtheta(:,length(theta)) =  dtheta(:,length(theta)-1);
 dz(:,length(z)) =  dz(:,length(z)-1);
 nsq = (g/theta0)*dtheta./dz;

%calculate dthetae/dz using forward differencing
 dthetae = diff(thetae,1,2);
 dthetae(:,length(thetae)) =  dthetae(:,length(thetae)-1);
 nsqe = (g/theta0)*dthetae./dz;


