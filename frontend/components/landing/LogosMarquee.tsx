"use client"
import React from 'react'

const logos = ['PostgreSQL','MySQL','MongoDB','SQL Server','Snowflake','BigQuery']

export default function LogosMarquee(){
  return (
    <section className="px-6 pb-12">
      <div className="mx-auto max-w-6xl">
        <div className="glass overflow-hidden rounded-2xl p-4">
          <div className="marquee">
            <div className="marquee-track">
              {logos.concat(logos).map((l, i)=> (
                <div key={i} className="marquee-item">{l}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
