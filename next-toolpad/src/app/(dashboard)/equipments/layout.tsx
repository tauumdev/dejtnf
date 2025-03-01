import React from 'react';

export default function Layout(props: { children: React.ReactNode }) {
    return (
        <div>
            {/* <div>Layout</div> */}
            {props.children}
        </div>
    );
}  
