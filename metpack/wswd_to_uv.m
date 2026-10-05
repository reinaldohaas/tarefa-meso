 function [u,v] = wswd_to_uv(ws, wd)
% function that takes wind speed and wind direction (deg from North)
% and converts to vectors (u,v)
% function [u,v] = wswd_to_uv(ws, wd)

u = ws.*cos((270-wd)*pi/180);
v = ws.*sin((270-wd)*pi/180);