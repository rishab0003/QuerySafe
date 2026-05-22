"use client"
import React from 'react'

const logos = ['PostgreSQL','MySQL','MongoDB','SQL Server','Snowflake','BigQuery']

export default function LogosMarquee(){
  return (
    <section className="px-6 pb-12">
      <div className="max-w-6xl mx-auto">
        <div className="glass p-4 rounded-2xl overflow-hidden">
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
