 function [vectormean_ws, vectormean_wd] = uv_to_vectormean(u,v)
% use [vectormean_ws, vectormean_wd] = uv_to_vectormean(u,v)
 % function that takes vectors (u,v) and calculates the  
% vector mean wind speed and wind direction 
% function [vectormean_ws, vectormean_wd] = uv_to_vectormean(u,v)

vectormean_ws = sqrt(mean(u)*mean(u) + mean(v)*mean(v));
vectormean_wd =  270 - (180/pi)*atan2(mean(v),mean(u));

if (vectormean_wd > 360) vectormean_wd = vectormean_wd - 360; end;
