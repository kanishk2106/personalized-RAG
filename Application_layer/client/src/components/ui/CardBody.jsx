import React from "react";

/** Renders a card's body: labeled ">" bullet points, or a plain paragraph. */
export function CardBody({ item }) {
  if (item.bullets) {
    return (
      <ul className="list-none m-0 mb-[14px] p-0 flex flex-col gap-[7px]">
        {item.bullets.map((b, i) => (
          <li
            key={i}
            className="relative pl-[18px] text-[14px] text-lede leading-[1.55] before:content-['>'] before:absolute before:left-0 before:top-0 before:text-green before:font-mono before:font-bold"
          >
            {b.k ? <><b className="text-amber font-bold">{b.k}:</b> {b.v}</> : b}
          </li>
        ))}
      </ul>
    );
  }
  return <p className="text-[15px] text-lede mb-[14px]">{item.what}</p>;
}
