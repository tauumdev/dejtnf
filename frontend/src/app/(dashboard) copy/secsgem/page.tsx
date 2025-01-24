import * as React from 'react';
import Typography from '@mui/material/Typography';
import { auth } from "../../../auth";

export default async function SecsgemPage() {
  const session = await auth();
  if (session?.user?.role === "admin") {
    return <Typography>You are an admin, welcome to SECS/GEM!</Typography>;
  }
  return <Typography>You are not authorized to view this page!</Typography>;
}
