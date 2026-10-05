function [filter999] = filter999(M)
% removes bad data points 999 from an array and replaces them with NaN

M(find(M==999)) = ones(length(find(M==999)), 1)*NaN;
filter999 = M;

