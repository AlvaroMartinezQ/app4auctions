interface USERGENERIC {
  email: string;
}

export interface USERLOGIN extends USERGENERIC {
  password: string;
}

export interface USERSINGUP extends USERLOGIN {
  identification_number: string;
  personal_name: string;
  personal_surname: string;
  country: string;
  address: string;
  phone: string;
}

export interface USERPROFILE extends USERGENERIC {
  identification_number: string | null;
  personal_name: string | null;
  personal_surname: string | null;
  country: string | null;
  address: string | null;
  phone: string | null;
}

export interface PASSWORDCHANGE {
  old_pwd: string | null;
  new_pwd: string | null;
  new_pwd_repeated: string | null;
}

export interface EMAILCHANGE {
  old_email: string | null,
  new_email: string | null,
}
