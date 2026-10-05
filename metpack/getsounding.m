 % Station ID (get from UWYO map -- e.g., KUIL: 72797):
 % http://weather.uwyo.edu/upperair/sounding.html
 % arhines@fas.harvard.edu
 
% Example usage with skewt.m:
% [data,header,status] = getsounding(72797,2008,5,12,12)
% skewt(data(:,1),data(:,3),data(:,5)/100) 
%
function [data,header,status] = getsounding(station_id,year,month,day,hour)
station_id = num2str(station_id);
header = {'P (hPa)','z (m)','T (C)','DWPT (C)','RELH (' ...
' %)','MIXR (g/kg)','DRCT (deg)','SKNT (kts)','THTA (K)', ...
		    'THTE (K)','THTV (K)'};
year_s = num2str(year);
if month < 10
  month_s = ['0' num2str(month)];
else
  month_s = num2str(month);
end
if day < 10
  day_s = ['0' num2str(day)];
else
  day_s = num2str(day);
end
if hour < 10
  hour_s = ['0' num2str(hour)];
else
  hour_s = num2str(hour);
end
  fid = fopen('header.txt','wt');
  [station_id hour month day year]
  fprintf(fid,'%s %d %d %d %d',num2str(station_id),hour,month,day,year)
  
  fclose(fid);
theurl = ['http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&' ...
	  'TYPE=TEXT:LIST&YEAR=' year_s '&MONTH=' month_s '&FROM=' day_s hour_s '&TO=' day_s hour_s '&STNM=' station_id]
[str, status] = urlread(theurl);
if length(str) < 900
    status = 0;
    data = NaN;
elseif status == 1
  fid = fopen('sounding.txt','wt');
  fprintf(fid,'%s',str);
  
  fclose(fid);
  
  kstart = findstr(str,'<PRE>');
  kend = findstr(str,'</PRE>');
  str = str(kstart(1)+318:kend(1)-2);
  fid = fopen('sounding_temp.txt','wt');
  fprintf(fid,'%s',str);
  fclose(fid);
  fid = fopen('sounding_temp.txt','r');
  tline = fgetl(fid);
  k = 1;
  data = NaN(1,11);
  while ischar(tline)
    data(k,:) = [str2n(tline(1:7)) str2n(tline(9:14)) str2n(tline(16:21)) str2n(tline(22:28)) str2n(tline(30:35)) str2n(tline(37:42)) str2n(tline(45:49)) str2n(tline(52:56)) str2n(tline(58:63)) str2n(tline(65:70)) str2n(tline(72:77))];
    tline = fgetl(fid);
    k = k+1;
  end
  fclose(fid);
else
  status = 0;  
  data = NaN;
  disp('Error: URL retrieval failed');
end
  fid = fopen('modsound.txt','wt');
  for i=1:k-1
  fprintf(fid,'%f %f %f\n',data(i,1),data(i,3),data(i,4))
  end
  fclose(fid);
end

function y = str2n(x)
  if isempty(str2num(x))
    y = NaN;
  else
    y = str2num(x);
  end
end
