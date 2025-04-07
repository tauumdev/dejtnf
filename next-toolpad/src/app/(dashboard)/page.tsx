import * as React from 'react';
import Typography from '@mui/material/Typography';
import { auth } from '../api/auth/auth';
import { Box } from '@mui/material';



export default async function HomePage() {
  const session = await auth();

  const jwt = await auth();
  // console.log(jwt?.user?.id);


  return (
    <Box>
      <Box>
        <Typography>
          Welcome to Toolpad, {session?.user?.name || 'User'}!
        </Typography>
        <Typography>
          Your role: {session?.user?.role || 'Unknown'}
        </Typography>
        {/* <pre>{JSON.stringify(session, null, 2)}</pre> */}
        {/* <pre>{JSON.stringify(jwt, null, 2)}</pre> */}
      </Box>
    </Box>
  );
}
