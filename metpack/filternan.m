function [filterNaN] = filterNaN(M)
% matlab code to remove NaN from matrix M

filterNaN = M(~isnan(M));
