export const getDateNow = () => {
  const d = new Date();
  const yyyy = d.getFullYear();
  let mm: string | number = d.getMonth() + 1;
  if (mm < 10) mm = '0' + mm;
  let dd: string | number = d.getDate();
  if (dd < 10) dd = '0' + dd;
  let h: string | number = d.getHours();
  if (h < 10) h = '0' + h;
  let m: string | number = d.getMinutes();
  if (m < 10) m = '0' + m;
  let s: string | number = d.getSeconds();
  if (s < 10) s = '0' + s;
  const now =
    yyyy + '-' + mm + '-' + dd + 'T' + h + ':' + m + ':' + s + '+00:00';
  return now;
};

export const getDateNowOffset = (offset: number) => {
  const d = new Date();
  const yyyy = d.getFullYear();
  let mm: string | number = d.getMonth() + 1;
  if (mm < 10) mm = '0' + mm;
  let dd: string | number = d.getDate();
  if (dd < 10) dd = '0' + dd;
  let h: string | number = d.getHours();
  if (h < 10) h = '0' + h;
  let m: string | number = d.getMinutes();
  m = m - offset; // minus `offset` minutes
  if (m < 10) m = '0' + m;
  let s: string | number = d.getSeconds();
  if (s < 10) s = '0' + s;
  const now =
    yyyy + '-' + mm + '-' + dd + 'T' + h + ':' + m + ':' + s + '+00:00';
  return now;
}

export const formatDate = (d: string) => {
  const dt = new Date(d);
  const yyyy = dt.getFullYear();
  let mm: string | number = dt.getMonth() + 1;
  if (mm < 10) mm = '0' + mm;
  let dd: string | number = dt.getDate();
  if (dd < 10) dd = '0' + dd;
  let h: string | number = dt.getUTCHours();
  if (h < 10) h = '0' + h;
  let m: string | number = dt.getMinutes();
  if (m < 10) m = '0' + m;
  const formatedDate = yyyy + '-' + mm + '-' + dd + ' ' + h + ':' + m;
  return formatedDate;
}

export const formatDateWSeconds = (d: string) => {
  const dt = new Date(d);
  const noSeconds = formatDate(d);
  let s: string | number = dt.getSeconds();
  if (s < 10) s = '0' + s;
  return noSeconds + ':' + s;
}
