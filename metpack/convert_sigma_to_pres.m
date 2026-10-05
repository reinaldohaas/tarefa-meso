function out = convert_sigma_to_pres(in, ps, newlevs);

hyam = [0.00480929994955659, 0.013073099777102, 0.032559100538492, ...
	0.0639470964670177, 0.0802583247423168, 0.0766648948192596, ...
	0.0720923840999599, 0.0664718076586719, 0.0598041415214539, ...
	0.0521853193640709, 0.0438226312398908, 0.035038441419601, ...
	0.0262589752674099, 0.017985042184591, 0.010747664608061, ...
	0.00505276303738358, 0.0013234377838671, 0]';


hybm = [0, 0, 0, 0, 0.018784884363413, 0.062048017978668, ...
	0.11709871888161, 0.18476781249046, 0.265043288469309, ...
	0.356770157814029, 0.457452863454819, 0.56321024894714, ...
	0.668910741806027, 0.768524885177609, 0.855659365653988, ...
	0.92422324419022, 0.96912252902985, 0.992528021335598]';

pnot = 1000;

nlev = length(hyam);
newlevs = newlevs(:);
nlev2 = length(newlevs);

%  Go through argument check.
dims_ps = ndims(ps);
dims_in = ndims(in);
size_ps = size(ps);
size_in = size(in);

if dims_ps ~= (dims_in - 1); 
  error('Variable ''in'' should have one more dimension than ''ps''.')
end

if size_in(2) ~= nlev;
  error(['Either ''in'' has an inconsistent level dimension, or the' ...
	 'order (ntim, nlev, nlat, nlon) is wrong.                 '])
end

%  Reshape so level is the first dimension
in = shiftdim(in, 1); 
in = reshape(in, size_in(2), prod(size_in)/nlev);

ps = shiftdim(ps, 1);
ps = reshape(ps, 1, prod(size_ps));

%  Check for size consistency
if size(ps, 2) ~= size(in, 2);
  error('Variables ''in'' and ''ps'' have inconsistent dimensions')
end

npts = prod(size_in)/nlev;

%  Now that ps is 2D, make sure units are in hPa:
if round(log10(mean(mean(ps)))) == 5;
  ps = ps/100;
end

%  Now, do interpolation
out = repmat(NaN, [nlev2 prod(size_in)/size_in(2)]);
plevs = pnot*hyam*ones(1, npts)+hybm*ps;

%  This method is considerably faster than the following - both produce
%  the same results.
for i = 1:nlev2;
  
  for j = 1:npts
    
    xup = sum(plevs(:,j) < newlevs(i));
    
    if xup < 18;
      out(i,j) = in(xup,j) + ...
	  (log(newlevs(i)) - log(plevs(xup,j))) * ...
	  (in(xup+1,j) - in(xup,j))/(log(plevs(xup+1,j))-log(plevs(xup,j)));
    end
    
  end
  
end

%  This method is considerably slower than the preceding
%for i = 1:npts
%  out(:, i) = interp1(log(plevs(:,i)), in(:,i), log(newlevs));
%end

%  Reshape back
out = reshape(out, [nlev2 size_in(3:end) size_in(1)]);
out = shiftdim(out, dims_in - 1);
